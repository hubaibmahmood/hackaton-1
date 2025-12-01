"MDX parser and chunker for content indexing."
import logging
from typing import List, Dict, Any, Optional
import frontmatter
import tiktoken
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode

from src.config import settings
from src.models.content import BookChunk, ChunkMetadata

logger = logging.getLogger(__name__)

class ContentChunker:
    """Parses MDX files and splits them into semantic chunks."""

    def __init__(self):
        """Initialize chunker with tokenizer and markdown parser."""
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.md = MarkdownIt()
        
        # Config from settings
        self.chunk_size = settings.chunk_size_tokens
        self.chunk_overlap = settings.chunk_overlap_tokens

    def parse_file(self, file_path: str) -> List[BookChunk]:
        """Parse an MDX file and return a list of chunk objects.
        
        Args:
            file_path: Path to the .md/.mdx file
            
        Returns:
            List of BookChunk objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            metadata = post.metadata
            content = post.content
            
            # Basic metadata enrichment
            # Extract basic info from file path if needed, e.g. chapter number
            # For now, rely on frontmatter
            
            return self._chunk_content(content, metadata, file_path)
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return []

    def _chunk_content(self, text: str, metadata: Dict[str, Any], source_url: str) -> List[BookChunk]:
        """Split content into chunks while preserving structure."""
        
        tokens = self.md.parse(text)
        node = SyntaxTreeNode(tokens)
        
        chunks = []
        current_section_stack = [] # Tracks [H1, H2, H3...] titles
        
        # We will traverse the tree and build semantic blocks
        # This is a simplified traversal that linearizes the document but tracks headers
        
        current_chunk_text = []
        current_chunk_tokens = 0
        
        # Heuristic: We iterate through top-level nodes (headers, paragraphs, lists, code blocks)
        for child in node.children:
            if child.type.startswith('heading'):
                # Update section context
                level = int(child.tag.replace('h', ''))
                text_content = self._get_node_text(child)
                
                # Adjust stack
                if level > len(current_section_stack):
                    current_section_stack.append(text_content)
                else:
                    current_section_stack = current_section_stack[:level-1]
                    current_section_stack.append(text_content)
                
                # Headers usually start a new logical block, but strictly splitting on every header 
                # might create tiny chunks. For RAG, capturing the header in the text is good.
                # We append the header to the current text flow.
                
                # Format header in markdown style for the chunk text
                header_md = f"{ '#' * level} {text_content}\n\n"
                self._add_to_chunk(chunks, header_md, current_chunk_text, metadata, current_section_stack, source_url)
                
            else:
                # Content node (paragraph, list, code_block, etc.)
                # We get the raw markdown/text reconstruction
                # Note: markdown-it doesn't easily give back raw markdown of a node range
                # We might need to extract it from the original text using map lines if available
                # Or reconstruct it. Reconstructing is safer for normalization.
                
                # For simplicity and robustness, let's grab the lines from the original source 
                # if map is present, otherwise simple text extraction.
                
                block_text = self._get_node_source_text(child, text)
                self._add_to_chunk(chunks, block_text + "\n\n", current_chunk_text, metadata, current_section_stack, source_url)

        # Flush remaining
        if current_chunk_text:
             self._finalize_chunk(chunks, current_chunk_text, metadata, current_section_stack, source_url)
             
        return chunks

    def _add_to_chunk(self, chunks, text, current_chunk_text, metadata, section_stack, source_url):
        """Add text to current chunk, splitting if necessary."""
        text_tokens = len(self.tokenizer.encode(text))
        current_tokens = len(self.tokenizer.encode("".join(current_chunk_text)))
        
        if current_tokens + text_tokens > self.chunk_size:
            # Current chunk is full, finalize it
            self._finalize_chunk(chunks, current_chunk_text, metadata, section_stack, source_url)
            current_chunk_text.clear()
            
            # If the new text block itself is larger than chunk size, we might need to split it hard
            # For now, we just start a new chunk with it (and it might exceed limit slightly, which is usually fine for RAG)
            # Or we could split strictly.
            
            # Handle overlap: We should actually pull back some text from previous chunk if possible
            # But simple logic: just start new chunk.
            pass
            
        current_chunk_text.append(text)

    def _finalize_chunk(self, chunks, text_list, metadata, section_stack, source_url):
        """Create a chunk object from accumulated text."""
        full_text = "".join(text_list).strip()
        if not full_text:
            return

        # Basic metadata extraction
        chapter_title = section_stack[0] if section_stack else metadata.get("title", "Unknown")
        section_title = section_stack[-1] if section_stack else "Introduction"
        
        # Create metadata object
        try:
            chunk_meta = ChunkMetadata(
                document_id=source_url, # Use path as ID for now
                document_path=source_url,
                document_url=source_url, # Todo: Convert to actual URL
                chapter_title=chapter_title,
                heading_path=section_stack,
                heading_level=len(section_stack),
                section_id=section_title.lower().replace(" ", "-"),
                chunk_index=len(chunks),
                chunk_id=f"{source_url}_{len(chunks)}",
                citation_text=f"{chapter_title} > {section_title}",
                citation_url=source_url, # Todo: Add anchor
                token_count=len(self.tokenizer.encode(full_text)),
                character_count=len(full_text)
            )
            
            chunk = BookChunk(
                chunk_id=chunk_meta.chunk_id,
                text=full_text,
                metadata=chunk_meta
            )
            chunks.append(chunk)
        except Exception as e:
            logger.warning(f"Failed to create chunk metadata: {e}")
            # Fallback or skip
            pass

    def _get_node_text(self, node) -> str:
        """Extract plain text from a node (recursive)."""
        if node.type == 'text':
            return node.content
        if node.type == 'code_inline':
            return node.content
        text = []
        if hasattr(node, 'children') and node.children:
            for child in node.children:
                text.append(self._get_node_text(child))
        return "".join(text)

    def _get_node_source_text(self, node, original_text: str) -> str:
        """Extract original source text for a node using map."""
        if node.map:
            start_line, end_line = node.map
            # Split original text by lines (inefficient for large docs, but robust)
            lines = original_text.splitlines(keepends=True)
            # markdown-it lines are 0-indexed
            return "".join(lines[start_line:end_line])
        
        # Fallback if no map (e.g. inline nodes, though we iterate blocks)
        # For blocks, markdown-it usually provides maps.
        return self._get_node_text(node)

# Global chunker instance
chunker = ContentChunker()
