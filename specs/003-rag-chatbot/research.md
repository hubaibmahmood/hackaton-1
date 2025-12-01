# Research Findings: RAG Chatbot Implementation

**Date**: 2025-12-01
**Feature**: 003-rag-chatbot
**Purpose**: Resolve technical unknowns identified in Phase 0 planning

---

## Research Task 1: Backend Deployment Platform Selection

### Decision: Render (**UPDATED** per user requirements)

**Rationale**:
- **Free Tier Available**: 750 instance hours/month (sufficient for educational use)
- **Built-in Cron Support**: Render Cron Jobs feature for daily indexing
- **Docker Support**: Native Docker deployment with Python 3.12
- **Simple Setup**: Git-based auto-deployment
- **Cost**: Free tier, $0/month (vs. paid alternatives)
- **Trade-off Accepted**: ~60-second cold starts after 15min inactivity (acceptable for educational traffic patterns)

**Alternatives Considered** (from original research):
1. **Google Cloud Run** ($0-5/month): Better cold starts (200-800ms) but user prefers Render/Railway
2. **Railway**: Eliminated - no free tier since August 2023
3. **Fly.io** ($3-10/month): Excellent cold starts but requires custom cron solution
4. **Azure Container Apps** ($0-8/month): More complex setup

**Implementation** (Python 3.12 + uv):
```bash
# render.yaml configuration
services:
  - type: web
    name: rag-chatbot
    runtime: docker
    dockerfilePath: ./Dockerfile
    envVars:
      - key: PYTHON_VERSION
        value: 3.12
      - key: QDRANT_URL
        fromEnvVar: QDRANT_URL
      - key: NEON_DB_URL
        fromEnvVar: NEON_DB_URL

# Render cron job (daily at 2 AM UTC)
  - type: cron
    name: daily-indexing
    schedule: "0 2 * * *"
    dockerCommand: "uv run python -m src.indexing.scheduler"
```

**uv Package Manager**:
- Fast, Rust-based Python package installer
- Uses `pyproject.toml` (no `requirements.txt`)
- Lockfile: `uv.lock` for reproducible builds
- Docker integration: Multi-stage builds with uv

---

## Research Task 2: OpenAI ChatKit SDK Availability and Integration

### Decision: OpenAI ChatKit SDK (@openai/chatkit-react) + OpenAI Agents SDK (**UPDATED** per user requirements)

**Backend**: **OpenAI Agents SDK** (Python)
**Frontend**: **OpenAI ChatKit SDK** (@openai/chatkit-react) with **React 19.x**

**Rationale**:
- **Agents SDK Benefits**:
  - Built-in tool calling and function execution
  - Structured agent orchestration for RAG workflows
  - Custom tools for Qdrant retrieval integration
  - Streaming support for real-time responses
  - Better error handling and retry logic

- **ChatKit SDK Benefits** (React 19.x compatible):
  - Official OpenAI UI components for chat interfaces
  - Production-ready features: streaming, markdown, code highlighting
  - React 19.x support with modern concurrent features
  - TypeScript-first with excellent DX
  - Seamless integration with Docusaurus

**Architecture** (Updated):
```
React 19.x/Docusaurus Frontend
    ↓ (OpenAI ChatKit SDK @openai/chatkit-react)
    ↓ HTTP/SSE to FastAPI
FastAPI Backend (Python 3.12 + uv)
    ↓ (OpenAI Agents SDK)
    ↓ Custom Tools → Qdrant Vector DB → Retrieval → Context
    ↓
OpenAI GPT-4 Turbo (via Agents SDK, streaming)
```

**Implementation Pattern** (Updated):
```typescript
// Frontend: OpenAI ChatKit with React 19.x
import { ChatProvider, ChatMessages, ChatInput } from '@openai/chatkit-react'

function ChatBot() {
  return (
    <ChatProvider
      apiUrl="/api/chat"  // FastAPI backend
      config={{
        model: "gpt-4-turbo",
        stream: true
      }}
    >
      <div className="chat-container">
        <ChatMessages />
        <ChatInput placeholder="Ask about the book..." />
      </div>
    </ChatProvider>
  )
}
```

```python
# Backend: FastAPI with OpenAI Agents SDK
from openai import OpenAI
from openai.agents import Agent, Tool

# Define custom Qdrant retrieval tool
def search_book_content(query: str) -> list[dict]:
    """Search book content using Qdrant vector database."""
    embeddings = generate_embedding(query)
    results = qdrant_client.search(
        collection_name="book_content",
        query_vector=embeddings,
        limit=5
    )
    return [{"text": r.payload["text"], "citation": r.payload["citation"]} for r in results]

# Create RAG agent with custom tools
agent = Agent(
    name="BookAssistant",
    model="gpt-4-turbo",
    instructions="You are a helpful assistant for the Physical AI textbook...",
    tools=[
        Tool(function=search_book_content, description="Search book content")
    ]
)

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # Run agent with streaming
    stream = agent.run(
        messages=request.messages,
        stream=True
    )

    return StreamingResponse(
        stream_generator(stream),
        media_type="text/event-stream"
    )
```

---

## Research Task 3: Docusaurus Content Extraction and Chunking Strategy

### Decision: Hybrid Semantic + Section-Based Chunking with MDX Parsing

**MDX Parsing Libraries**:
- **@mdx-js/mdx** (v3+): Core MDX compiler
- **remark-mdx**, **remark-frontmatter**, **remark-gfm**: unified plugins
- **mdast-util-to-string**: Convert AST to plain text
- **gray-matter**: Extract YAML frontmatter

**Chunking Strategy**: Hybrid Approach
1. **Primary**: Section-based splitting at H2/H3 headers (maintains coherence)
2. **Secondary**: Semantic chunking for oversized sections (LangChain SemanticChunker)

**Optimal Chunk Size**: **400-500 tokens** (~1,600-2,000 characters)

**Rationale**:
- Technical documentation with code examples benefits from larger chunks
- Captures full API descriptions and complete explanations
- RecursiveCharacterTextSplitter with 400-512 tokens achieved 85-90% recall in benchmarks
- Complex robotics concepts require broader context

**Overlap Strategy**: **10-15% overlap (50-75 tokens)**

**Rationale**:
- Industry best practice for continuity
- Prevents concept fragmentation at chunk boundaries
- For 500-token chunks: 60-75 token overlap ensures coherence

**Code Block Handling**: **Include code blocks with enhanced metadata**

**Rationale**:
- Code examples are integral to technical understanding
- Modern embedding models (e.g., text-embedding-3-small) handle code well
- Code provides concrete implementation context for abstract concepts
- Educational content requires prose + code together

**Implementation Configuration**:
```typescript
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter'

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 2000,        // ~500 tokens (4 chars/token)
  chunkOverlap: 300,      // ~75 tokens (15% overlap)
  separators: ['\n## ', '\n### ', '\n\n', '\n', ' ', ''],
})
```

**Metadata Schema**:
```typescript
interface ChunkMetadata {
  // Document identification
  documentId: string
  documentPath: string      // /docs/part-01-physical-ai/chapter-01/index.md
  documentUrl: string       // /docs/part-01-physical-ai/chapter-01

  // Hierarchical structure
  partNumber: number
  partName: string
  chapterNumber: number
  chapterTitle: string

  // Content structure
  headingPath: string[]     // ["What is Physical AI?", "Definition"]
  headingLevel: number      // 2 or 3
  sectionId: string         // "what-is-physical-ai-definition"

  // Chunk positioning
  chunkIndex: number
  chunkId: string          // "part01-ch01-chunk-003"

  // Content characteristics
  contentType: string      // "explanation" | "example" | "exercise"
  containsCode: boolean
  codeLanguages: string[]
  containsTable: boolean

  // Citation
  citationText: string     // "Chapter 1, Section: What is Physical AI?"
  citationUrl: string      // Full URL with anchor

  // Metrics
  tokenCount: number
  characterCount: number
}
```

**Source Attribution Example**:
```json
{
  "citationText": "Part 1: Physical AI | Chapter 1: Overview | What is Physical AI?",
  "citationUrl": "https://hubaibmahmood.github.io/hackaton-1/docs/part-01-physical-ai/chapter-01#what-is-physical-ai"
}
```

---

## Research Task 4: Text Selection Integration Pattern

### Decision: Custom React Hook with Selection API + Floating UI

**Recommended Approach**: Custom implementation using Web APIs + Floating UI library

**Rationale**:
- Browser Selection API is mature and well-supported
- Floating UI provides robust positioning logic
- Lightweight solution without heavy dependencies
- Full control over UX and integration with Assistant UI chatbot

**Libraries**:
- **@floating-ui/react** (v0.26+): Positioning engine for context menu
- Browser native **Selection API**: Detect text selection
- **React hooks**: Custom `useTextSelection` hook

**Implementation Pattern**:
```typescript
import { useFloating, autoUpdate, offset, flip, shift } from '@floating-ui/react'

function useTextSelection() {
  const [selection, setSelection] = useState<Selection | null>(null)
  const [selectedText, setSelectedText] = useState('')

  useEffect(() => {
    const handleSelectionChange = () => {
      const sel = window.getSelection()
      if (sel && sel.toString().trim().length > 0) {
        setSelection(sel)
        setSelectedText(sel.toString())
      } else {
        setSelection(null)
        setSelectedText('')
      }
    }

    document.addEventListener('selectionchange', handleSelectionChange)
    return () => document.removeEventListener('selectionchange', handleSelectionChange)
  }, [])

  return { selection, selectedText, hasSelection: selectedText.length > 0 }
}

// Context menu component
function SelectionContextMenu() {
  const { selection, selectedText, hasSelection } = useTextSelection()
  const { refs, floatingStyles } = useFloating({
    open: hasSelection,
    middleware: [offset(10), flip(), shift()],
    whileElementsMounted: autoUpdate,
  })

  if (!hasSelection) return null

  return (
    <div ref={refs.setFloating} style={floatingStyles}>
      <button onClick={() => openChatbotWithSelection(selectedText)}>
        Ask about this selection
      </button>
    </div>
  )
}
```

**Mobile Support**: Use `touchend` and `touchstart` events:
```typescript
// Detect mobile text selection
document.addEventListener('touchend', () => {
  setTimeout(() => {
    const sel = window.getSelection()
    if (sel && sel.toString()) {
      showContextMenu(sel)
    }
  }, 10)
})
```

**Docusaurus Integration**:
- Add `SelectionContextMenu` component to theme wrapper
- Use Docusaurus `@docusaurus/theme-common` for theme consistency
- Swizzle layout component if needed for global integration

**Alternative Considered**: **react-text-selection-popover**
- More batteries-included but less flexible
- Harder to integrate with custom chatbot UI
- Custom solution provides better control

---

## Research Task 5: Embedding Model Selection

### Decision: OpenAI text-embedding-3-small API

**Rationale**:
- **Quality**: Superior performance (62.3% MTEB score) vs. open-source alternatives
- **Cost Efficiency**: $0.02 per 1M tokens = ~$0.20-1.00 for full book indexing (10K-50K chunks)
- **No Infrastructure**: Serverless, no hosting costs or maintenance
- **Latency**: Fast query-time embedding (<100ms)
- **Qdrant Compatibility**: Native support, 1536 dimensions
- **Consistency**: Same model for indexing and query embeddings (critical for RAG)

**Cost Analysis** (for 10K-50K chunks):
- **Indexing**: 50K chunks × 500 tokens/chunk = 25M tokens × $0.02/1M = **$0.50 one-time**
- **Query Embeddings**: 10K queries/month × 50 tokens = 500K tokens × $0.02/1M = **$0.01/month**
- **Total**: <$1/month operational cost

**Alternatives Considered**:
1. **all-MiniLM-L6-v2** (sentence-transformers): Free but requires hosting compute, lower quality (42.7% MTEB), 384 dimensions
2. **text-embedding-3-large**: Higher quality (64.6% MTEB) but 4x cost ($0.13/1M tokens) - unnecessary for educational content
3. **Cohere embed-english-v3.0**: Competitive quality but $0.10/1M tokens (5x more expensive)

**Implementation**:
```python
from openai import OpenAI

client = OpenAI()

# Index-time: Batch embed book chunks
def embed_chunks(chunks: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks,
        dimensions=1536  # Default for text-embedding-3-small
    )
    return [d.embedding for d in response.data]

# Query-time: Embed user question
def embed_query(question: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[question]
    )
    return response.data[0].embedding
```

**Qdrant Configuration**:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Create collection
client.create_collection(
    collection_name="book_content",
    vectors_config=VectorParams(
        size=1536,           # text-embedding-3-small dimensions
        distance=Distance.COSINE
    )
)
```

---

## Research Task 6: Session Management Without Authentication

### Decision: UUID-based Session Tokens with HTTP-only Cookies

**Strategy**: Generate cryptographically secure UUIDs for session identification without user accounts

**Rationale**:
- **No PII**: Complies with privacy assumption (no user authentication required)
- **Secure**: Cryptographic randomness prevents session prediction/hijacking
- **Simple**: No OAuth/JWT complexity
- **Browser-Friendly**: HTTP-only cookies prevent XSS attacks
- **Expiry Support**: Built-in expiration (24 hours) via cookie `Max-Age`

**Implementation**:

**Backend (FastAPI)**:
```python
import uuid
from datetime import timedelta
from fastapi import FastAPI, Response, Cookie

app = FastAPI()

SESSION_EXPIRY = timedelta(hours=24)

@app.post("/api/chat")
async def chat(
    response: Response,
    session_id: str | None = Cookie(None),
    request: ChatRequest
):
    # Create new session if none exists
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=int(SESSION_EXPIRY.total_seconds()),
            httponly=True,      # Prevent XSS
            secure=True,        # HTTPS only
            samesite="lax",     # CSRF protection
        )

    # Load/create session
    session = await get_or_create_session(session_id)

    # Check rate limiting
    if not check_rate_limit(session):
        raise HTTPException(429, "Rate limit exceeded")

    # Process chat request
    return await process_chat(session, request)
```

**Session Schema (Neon Postgres)**:
```sql
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '24 hours',

    -- Rate limiting
    query_count INTEGER NOT NULL DEFAULT 0,
    last_query_window TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Conversation context
    conversation_history JSONB NOT NULL DEFAULT '[]'::jsonb,
    current_page_url TEXT,

    -- Metadata (no PII)
    user_agent TEXT,
    preferred_language TEXT DEFAULT 'en'
);

-- Auto-cleanup expired sessions
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

**Rate Limiting Logic**:
```python
async def check_rate_limit(session: Session) -> bool:
    """10 queries per minute per session"""
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=1)

    # Reset counter if outside window
    if session.last_query_window < window_start:
        session.query_count = 0
        session.last_query_window = now

    # Check limit
    if session.query_count >= 10:
        return False

    # Increment counter
    session.query_count += 1
    session.last_activity = now
    await session.save()

    return True
```

**Frontend (React)**:
```typescript
// Session is automatically managed via cookies
// No manual token handling needed

async function sendChatMessage(message: string) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    credentials: 'include',  // Send cookies automatically
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message })
  })

  return response.json()
}
```

**Session Expiry**:
- **24-hour timeout**: Cookie `Max-Age` handles automatic expiry
- **Browser close detection**: Frontend can call `/api/session/close` on `beforeunload`
- **Background cleanup**: Cron job deletes expired sessions from Postgres

**Security Considerations**:
- **HTTP-only cookies**: Prevents JavaScript access (XSS protection)
- **Secure flag**: HTTPS-only transmission
- **SameSite=Lax**: CSRF protection while allowing navigation
- **No sensitive data**: Session only stores conversation history (no PII)

**Alternative Considered**: localStorage with JWT
- Vulnerable to XSS attacks
- Requires manual expiry handling
- More complex for simple use case

---

## Summary of Decisions

| Research Area | Decision | Rationale |
|---------------|----------|-----------|
| **Deployment Platform** | Render (free tier) | 750 instance hours/month, built-in cron, Docker + Python 3.12 support, $0/mo - **UPDATED** per user requirements |
| **Backend SDK** | OpenAI Agents SDK | Tool calling, custom Qdrant retrieval, structured orchestration, streaming - **UPDATED** per user requirements |
| **Frontend SDK** | OpenAI ChatKit SDK (@openai/chatkit-react) | Official UI components, React 19.x support, production-ready - **UPDATED** per user requirements |
| **Python Version** | Python 3.12 | Latest stable release - **UPDATED** per user requirements |
| **Package Manager** | uv (Rust-based) | Fast, reproducible builds, pyproject.toml + uv.lock - **UPDATED** per user requirements |
| **React Version** | React 19.x | Latest with concurrent features, Docusaurus compatibility - **UPDATED** per user requirements |
| **MDX Parsing** | unified/remark ecosystem | Native MDX support, mature, handles JSX components |
| **Chunking Strategy** | Hybrid semantic + section-based | 400-500 tokens, 10-15% overlap, maintains coherence |
| **Code Handling** | Include with metadata | Educational context requires prose + code together |
| **Chunk Metadata** | Hierarchical + citations | Part > chapter > section structure, URL anchors for citations |
| **Text Selection UI** | Custom hook + Floating UI | Lightweight, full control, native Selection API |
| **Embedding Model** | OpenAI text-embedding-3-small | Superior quality (62.3% MTEB), $0.02/1M tokens, ~$1/mo operational cost |
| **Session Management** | UUID + HTTP-only cookies | No PII, secure, simple, 24hr auto-expiry |

**Architecture Stack** (Updated):
- **Backend**: FastAPI (Python 3.12 + uv) + OpenAI Agents SDK + Qdrant + Neon Postgres
- **Frontend**: Docusaurus 3.x + React 19.x + OpenAI ChatKit SDK + TypeScript 5.x
- **Deployment**: Render (backend, free tier) + GitHub Pages (frontend static)
- **AI/ML**: OpenAI GPT-4 Turbo (via Agents SDK) + text-embedding-3-small
- **Infrastructure**: Qdrant Cloud Free Tier (1GB) + Neon Serverless Free Tier (0.5GB)

---

## Next Steps

With all research completed, proceed to **Phase 1: Design & Contracts**:
1. Generate `data-model.md` with entity schemas
2. Create `contracts/openapi.yaml` for FastAPI API spec
3. Create `contracts/frontend-api.ts` for TypeScript interfaces
4. Write `quickstart.md` for developer setup
5. Update agent context with selected technologies
6. Re-validate Constitution Check

---

**Research Complete**: ✅ All 6 tasks resolved
**Date**: 2025-12-01
**Ready for**: Phase 1 Design
