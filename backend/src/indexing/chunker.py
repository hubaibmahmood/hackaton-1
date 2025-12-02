"MDX parser and chunker for content indexing."
import logging
import re
from typing import List, Dict, Any, Optional
import frontmatter
import tiktoken
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode
from pathlib import Path

from src.config import settings
from src.models.content import BookChunk, ChunkMetadata

logger = logging.getLogger(__name__)

class ContentChunker:
    """Parses MDX files and splits them into semantic chunks."""

    def __init__(self):
        """Initialize chunker with tokenizer and markdown parser."""
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.md = MarkdownIt()
        
        # Determine project root and Docusaurus docs root once
        # Assuming current file is backend/src/indexing/chunker.py
        # Path(__file__).resolve() -> .../book-generation/backend/src/indexing/chunker.py
        # .parent (chunker.py) -> .../book-generation/backend/src/indexing
        # .parent (indexing) -> .../book-generation/backend/src
        # .parent (src) -> .../book-generation/backend
        # .parent (backend) -> .../book-generation (project root)
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent
        self.docusaurus_docs_root = self.project_root / "book" / "docs"
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
            # Generate stable section_id and chunk_id
            section_id = section_title.lower().replace(" ", "-").replace(":", "") # Basic slugify
            chunk_id = f"{Path(source_url).stem}-{section_id}-{len(chunks)}"

            doc_url = self._generate_docusaurus_url(source_url)
            citation_url_with_anchor = self._generate_docusaurus_url(source_url, section_id)
            
            # Determine context
            prereqs, nexts = self._determine_context(Path(source_url))
            
            chunk_meta = ChunkMetadata(
                document_id=chunk_id, # Use generated chunk_id as document_id
                document_path=source_url,
                document_url=doc_url,
                chapter_title=chapter_title,
                heading_path=section_stack,
                heading_level=len(section_stack),
                section_id=section_id,
                chunk_index=len(chunks),
                chunk_id=chunk_id,
                citation_text=f"{chapter_title} > {section_title}",
                citation_url=citation_url_with_anchor,
                token_count=len(self.tokenizer.encode(full_text)),
                character_count=len(full_text),
                prerequisite_chapters=prereqs,
                next_topics=nexts
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

    def _determine_context(self, file_path: Path) -> tuple[list[str], list[str]]:
        """Determine prerequisites and next topics based on file path structure."""
        prerequisites = []
        next_topics = []
        
        try:
            # Convert to relative path from docs root
            try:
                rel_path = file_path.relative_to(self.docusaurus_docs_root)
            except ValueError:
                # Fallback if file is not in docs root (e.g. during testing)
                return [], []

            parts = rel_path.parts
            if not parts:
                return [], []

            # specific logic for part-XX/chapter-YY
            current_part_num = 0
            current_chapter_num = 0
            
            # regex for part-XX-name or part-XX
            part_match = re.match(r"part-(\d+)(?:-.*)?", parts[0])
            if part_match:
                current_part_num = int(part_match.group(1))
                
                # Add previous parts as prerequisites
                for i in range(1, current_part_num):
                    prerequisites.append(f"Part {i}")

            if len(parts) > 1:
                # regex for chapter-YY-name
                chapter_match = re.match(r"chapter-(\d+)(?:-.*)?", parts[1])
                if chapter_match:
                    current_chapter_num = int(chapter_match.group(1))
                    # Add previous chapters in same part
                    for i in range(1, current_chapter_num):
                         prerequisites.append(f"Part {current_part_num}, Chapter {i}")
            
            if current_chapter_num > 0:
                 next_topics.append(f"Part {current_part_num}, Chapter {current_chapter_num + 1}")
            elif current_part_num > 0:
                 # If we are at part root (intro), next is chapter 1
                 next_topics.append(f"Part {current_part_num}, Chapter 1")
                 
            # Also suggest next part
            if current_part_num > 0:
                next_topics.append(f"Part {current_part_num + 1}")

        except Exception as e:
            logger.warning(f"Context determination failed: {e}")
            
        return prerequisites, next_topics

    def _generate_docusaurus_url(self, file_path: str, section_id: Optional[str] = None) -> str:
        """Converts a local file path to a Docusaurus URL.
        
        Example: /path/to/project/book/docs/part-01-physical-ai/chapter-01-physical-ai-overview/index.md
        Goal: /docs/part-01-physical-ai/chapter-01-physical-ai-overview
        """
        # Ensure file_path is a Path object for easier manipulation
        path_obj = Path(file_path)
        
        # Log paths for debugging
        logger.debug(f"Path object for URL generation: {path_obj}")
        logger.debug(f"Relative to path: {Path.cwd() / 'book' / 'docs'}")

        # Find the 'docs' part in the path
        try:
            # Assumes 'book/docs' is the root for Docusaurus docs
            relative_to_docs = path_obj.relative_to(self.docusaurus_docs_root)
        except ValueError:
            logger.warning(f"File path {file_path} is not under {self.docusaurus_docs_root}. Cannot generate Docusaurus URL.")
            return "" # Return empty string or fallback

        url_parts = []
        for part in relative_to_docs.parts:
            if part.endswith(('.md', '.mdx')):
                part = part[:-len('.md')] if part.endswith('.md') else part[:-len('.mdx')]
            if part == 'index':
                continue
            url_parts.append(part)
        
        base_url = settings.docusaurus_base_url + "docs/" + "/".join(url_parts)
        
        if section_id:
            return f"{base_url}#{section_id}"
        return base_url

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
