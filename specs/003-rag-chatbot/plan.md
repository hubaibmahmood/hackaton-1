# Implementation Plan: Integrated RAG Chatbot

**Branch**: `003-rag-chatbot` | **Date**: 2025-12-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build and embed a Retrieval-Augmented Generation (RAG) chatbot within the published Docusaurus book to enable interactive learning. The chatbot will answer reader questions about book content using semantic search over indexed book material, support text selection queries, maintain conversation context, and provide source citations. The system uses OpenAI Agents/ChatKit SDKs for conversational AI, FastAPI for the backend API, Neon Serverless Postgres for session storage, and Qdrant Cloud Free Tier for vector embeddings.

## Technical Context

**Language/Version**: Python 3.12 (FastAPI backend), TypeScript 5.x (React/Docusaurus frontend integration)
**Package Management**: uv (Python package manager - fast, reliable, Rust-based)
**Primary Dependencies**:
- Backend: FastAPI 0.104+, OpenAI Agents SDK, Qdrant Client 1.7+, psycopg3 (Neon Postgres), Pydantic 2.x
- Frontend: React 19.x, Docusaurus 3.x, OpenAI ChatKit SDK (@openai/chatkit-react)
- ML/AI: OpenAI GPT-4 Turbo API (via Agents SDK), OpenAI text-embedding-3-small for vector generation

**Storage**:
- Vector Database: Qdrant Cloud Free Tier (vector embeddings for book content)
- Relational Database: Neon Serverless Postgres (conversation sessions, rate limiting counters)
- Content Source: Docusaurus markdown/MDX files

**Testing**:
- Backend: pytest, pytest-asyncio, httpx (FastAPI test client)
- Frontend: Jest, React Testing Library
- Integration: End-to-end tests for query-response flows

**Target Platform**:
- Backend: Render (free tier: 750 instance hours/month, auto-sleeps after 15min inactivity, ~60s cold start)
- Frontend: Static web (Docusaurus-generated site hosted on GitHub Pages)
- Deployment: Backend on Render with Docker (Python 3.12), Frontend on GitHub Pages
- Note: Railway eliminated as option (no free tier since Aug 2023)

**Project Type**: Web application (backend API + frontend integration)

**Performance Goals**:
- Query response time: <3 seconds p95 (per SC-002)
- Concurrent users: 100+ without degradation (per SC-007)
- Embedding search: <500ms p95 for vector similarity search
- API throughput: 10 requests/minute per session (rate limit from clarifications)

**Constraints**:
- Free tier limitations: Qdrant Cloud Free Tier (1GB storage, 100K vectors), Neon Serverless Free Tier (0.5GB storage)
- Session retention: Maximum 24 hours or browser close
- Rate limiting: 10 queries per minute per session
- Content indexing: Daily batch job during off-peak hours
- No PII collection: Session data only, no user authentication required

**Scale/Scope**:
- Book content: ~50-100 pages/chapters (estimated based on textbook structure)
- Concurrent readers: 100-999 (hundreds, per clarifications)
- Vector embeddings: ~10K-50K chunks (estimated based on book size with 500-token chunks)
- Daily API requests: ~5K-10K queries (assuming 10-20 queries per active reader)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle IX: Embedded RAG Chatbot for Interactive Learning
✅ **PASS** - This feature directly implements Constitution Principle IX: "An integrated RAG chatbot, built with OpenAI Agents/ChatKit SDKs, FastAPI, Neon Serverless Postgres, and Qdrant Cloud Free Tier, must be embedded within the published book."

**Alignment**:
- Uses specified tech stack (OpenAI Agents/ChatKit, FastAPI, Neon Postgres, Qdrant)
- Embeds within published Docusaurus book
- Answers questions about book content including user-selected text
- Enhances interactive learning experience

### Principle VI: Learning Outcomes Driven Content
✅ **PASS** - The chatbot enhances learning outcomes by providing immediate clarification on textbook content without disrupting study flow.

**Alignment**:
- Supports all six learning outcomes by enabling just-in-time knowledge retrieval
- Helps students understand Physical AI principles, ROS 2 concepts, simulation techniques, NVIDIA Isaac, HRI design, and conversational robotics through interactive Q&A
- Reduces friction in learning process

### Principle VIII: AI/Spec-Driven Book Creation with Spec-Kit Plus
✅ **PASS** - This feature follows Spec-Driven Development using Spec-Kit Plus workflow (spec.md → clarifications → plan.md → tasks.md).

**Alignment**:
- Detailed specification created via `/sp.specify`
- Clarifications resolved via `/sp.clarify`
- Current planning phase via `/sp.plan`
- Will generate testable tasks via `/sp.tasks`

### Principle X: Content Quality and Academic Integrity
✅ **PASS** - The RAG chatbot implements comprehensive safeguards to maintain academic integrity and prevent hallucinations.

**Safeguards Implemented**:
- FR-006: System must clearly indicate when questions fall outside book scope (prevents fabricated answers)
- SC-004: 85% accuracy requirement for detecting out-of-scope questions (measurable hallucination prevention)
- FR-007: All answers must include source citations to book content (enables verification and attribution)
- FR-008: Responses use current version of book content via daily re-indexing (ensures accuracy)
- FR-002: Retrieval-first architecture - answers are grounded in actual book content, not generated from memory

**Verification Mechanisms**:
- Test suite with known-correct answers from book content
- Citation accuracy validation (SC-003: 80% of responses must include citations)
- Out-of-scope detection testing (edge case validation)
- Confidence scoring for retrieval quality (vector similarity thresholds)
- Source attribution required for all answers (no unsourced claims)

**Architecture Design for Integrity**:
- OpenAI Agents SDK with custom Qdrant retrieval tools ensures RAG-first approach
- Embeddings match query to actual book passages before generation
- Response synthesis includes retrieved context + source metadata
- No open-ended generation without grounding in book content

## Project Structure

### Documentation (this feature)

```text
specs/003-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── openapi.yaml    # FastAPI backend API spec
│   └── frontend-api.ts  # TypeScript interfaces for frontend integration
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (backend + frontend)

backend/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── chat.py            # Chat endpoint (OpenAI Agents SDK integration)
│   │   ├── health.py          # Health check endpoint
│   │   └── middleware.py      # Rate limiting, CORS
│   ├── agents/                # OpenAI Agents SDK integration
│   │   ├── __init__.py
│   │   ├── rag_agent.py       # RAG agent with custom retrieval tools
│   │   └── tools.py           # Custom tools for Qdrant retrieval
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── embedding_service.py # Vector embedding generation (OpenAI API)
│   │   ├── retrieval_service.py # Qdrant vector search
│   │   └── session_service.py  # Session management, rate limiting
│   ├── models/                # Pydantic data models
│   │   ├── __init__.py
│   │   ├── query.py           # Query, Response models
│   │   ├── session.py         # UserSession model
│   │   └── content.py         # BookContent, SourceCitation models
│   ├── database/              # Database clients
│   │   ├── __init__.py
│   │   ├── postgres.py        # Neon Postgres connection (asyncpg)
│   │   └── qdrant.py          # Qdrant client setup
│   ├── indexing/              # Content indexing
│   │   ├── __init__.py
│   │   ├── indexer.py         # Main indexing orchestrator
│   │   ├── chunker.py         # MDX content chunking (unified/remark)
│   │   └── scheduler.py       # Daily indexing job (Render cron)
│   └── config.py              # Configuration (Pydantic settings)
├── tests/
│   ├── unit/                  # Unit tests
│   │   ├── test_agents.py     # Test OpenAI Agents
│   │   ├── test_embedding_service.py
│   │   └── test_session_service.py
│   ├── integration/           # Integration tests
│   │   ├── test_api_endpoints.py
│   │   └── test_rag_flow.py
│   └── fixtures/              # Test data
│       └── sample_book_content.md
├── .python-version            # Python 3.12 specification for uv
├── pyproject.toml             # uv project config with all dependencies
├── uv.lock                    # uv lockfile (auto-generated, committed)
└── Dockerfile                 # Multi-stage build with uv

book/
├── src/
│   ├── components/
│   │   ├── ChatBot/           # OpenAI ChatKit SDK integration
│   │   │   ├── ChatBot.tsx    # Main chatbot widget (ChatKit components)
│   │   │   ├── ChatProvider.tsx # ChatKit provider wrapper
│   │   │   ├── FloatingButton.tsx # Floating action button trigger
│   │   │   ├── SelectionMenu.tsx # Text selection context menu
│   │   │   └── ChatBot.css    # Chatbot styling (Docusaurus theme compatible)
│   │   └── ...
│   ├── hooks/
│   │   └── useTextSelection.ts # Custom hook for text selection
│   ├── services/
│   │   └── chatService.ts     # API client for FastAPI backend
│   └── theme/
│       └── ChatBotTheme.ts    # Theme customization for ChatKit
├── package.json               # React 19.x, @openai/chatkit-react dependencies
├── docusaurus.config.ts       # Updated with chatbot plugin
├── tests/
│   └── ChatBot.test.tsx       # Frontend component tests
└── ...

scripts/
└── index-content.sh           # Daily indexing trigger script
```

**Structure Decision**: Web application structure with separate backend (FastAPI Python 3.12 with uv) and frontend (Docusaurus React 19.x with TypeScript).

**Key Architectural Choices**:
- **Backend**: Uses uv package manager for fast, reproducible dependency management (pyproject.toml, uv.lock)
- **OpenAI Integration**: OpenAI Agents SDK for RAG orchestration, ChatKit SDK (@openai/chatkit-react) for frontend
- **Deployment**: Backend containerized with Docker (multi-stage uv build) for Render deployment
- **Frontend**: ChatKit components integrated into Docusaurus theme with custom text selection hooks
- **Indexing**: Daily scheduled job via Render cron (calls /api/index endpoint)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations requiring justification. All Constitution principles are satisfied.

## Specification Requirements Mapping

**Verification against spec.md** (all 18 functional requirements addressed):

| Spec Requirement | Plan Component | Implementation Approach |
|------------------|----------------|------------------------|
| FR-001: Always-accessible chatbot with dual activation | Frontend ChatBot/ components | ChatKit FloatingButton + SelectionMenu with @floating-ui |
| FR-002: Retrieve and cite book content | Backend agents/rag_agent.py | OpenAI Agents SDK with custom Qdrant retrieval tools |
| FR-003: Natural language processing | OpenAI Agents SDK | GPT-4 Turbo via Agents SDK (built-in NLP) |
| FR-004: Handle text selection as context | Frontend useTextSelection hook | Browser Selection API + pass to backend |
| FR-005: Maintain conversation history | Backend services/session_service.py + Neon Postgres | UUID sessions, 24hr expiry, JSONB storage |
| FR-006: Indicate out-of-scope questions | Backend agents/rag_agent.py | Agent instructions + confidence scoring |
| FR-007: Provide source citations | Backend agents/tools.py | Metadata in Qdrant chunks → citations in responses |
| FR-008: Current version content | Backend indexing/scheduler.py | Daily re-indexing via Render cron |
| FR-009: Multiple concurrent sessions | Backend session_service.py | UUID-based isolation, separate Postgres rows |
| FR-010: Handle code, diagrams, concepts | Backend indexing/chunker.py | MDX parsing with code block preservation |
| FR-011: Acceptable response time (<3s p95) | Google Cloud Run → **CHANGED TO** Render | Free tier with managed scaling |
| FR-012: Persist conversation for session | Backend database/postgres.py | Neon Postgres with 24hr/browser close expiry |
| FR-013: Support query types (definitions, etc.) | OpenAI Agents SDK | GPT-4 Turbo handles varied query types |
| FR-014: Process text selections (words→paragraphs) | Frontend useTextSelection | Selection API handles all lengths |
| FR-015: Semantic understanding | Backend services/embedding_service.py | OpenAI text-embedding-3-small (62.3% MTEB) |
| FR-016: Daily re-indexing | Backend indexing/scheduler.py | Render cron job calling /api/index |
| FR-017: Rate limiting (10 queries/min/session) | Backend middleware.py + session_service.py | Counter in Postgres, middleware enforcement |
| FR-018: Graceful degradation | Backend api/chat.py | Try-catch with friendly error, preserve context |

**All 10 Success Criteria addressed** (SC-001 through SC-010) via performance goals and constraints in Technical Context.

**All 4 User Stories covered** (P1-P4) via architecture:
- P1: General Questions → OpenAI Agents SDK + Qdrant retrieval
- P2: Text Selection → useTextSelection hook + ChatKit integration
- P3: Contextual Assistance → Agent can access page context + chapter metadata
- P4: Search/Discovery → Qdrant semantic search + chapter/section metadata

## Phase 0: Research ✅ COMPLETED

**Status**: All 6 research tasks completed. Findings documented in `research.md`.

**Decisions Made**:

1. **Deployment Platform**: Render (free tier: 750hrs/month, built-in cron, Docker support) - **Note**: Railway eliminated (no free tier)
2. **OpenAI Integration**: OpenAI Agents SDK (backend) + ChatKit SDK (frontend @openai/chatkit-react)
3. **MDX Chunking**: Hybrid semantic + section-based (400-500 tokens, unified/remark ecosystem)
4. **Text Selection**: Custom useTextSelection hook + @floating-ui/react for positioning
5. **Embeddings**: OpenAI text-embedding-3-small ($0.02/1M tokens, 62.3% MTEB)
6. **Sessions**: UUID + HTTP-only cookies (no PII, 24hr expiry, Postgres storage)

**Updated Decisions** (from user requirements):
- **Python Version**: 3.12 (originally 3.11+)
- **Package Manager**: uv (Rust-based, fast) instead of pip
- **React Version**: 19.x (originally 18.x)
- **Frontend SDK**: OpenAI ChatKit SDK (@openai/chatkit-react) confirmed
- **Backend SDK**: OpenAI Agents SDK confirmed

Full research details and alternatives considered: See `research.md`

## Phase 1: Design & Contracts (NEXT - Ready to Execute)

**Prerequisites**: ✅ Phase 0 research completed

**Outputs**:
- `data-model.md`: Entity schemas (UserSession, Query, Response, BookContent, SourceCitation)
- `contracts/openapi.yaml`: FastAPI backend API spec with OpenAI Agents SDK endpoints
- `contracts/frontend-api.ts`: TypeScript interfaces for ChatKit integration
- `quickstart.md`: Developer setup (uv installation, Render deployment, ChatKit config)

**Estimated Duration**: 1-2 days

## Implementation Phases & Dependencies

### Phase 2: Backend Core (Week 1-2)

**Dependencies**: Phase 1 contracts complete

**Parallel Work Opportunities**:
- **Track A (Backend Infrastructure)**: Can run in parallel
  - Setup uv project structure (`pyproject.toml`, `.python-version`)
  - Configure Neon Postgres connection
  - Configure Qdrant Cloud client
  - Environment configuration (Pydantic settings)

- **Track B (OpenAI Integration)**: Can run in parallel
  - OpenAI Agents SDK setup
  - Define custom retrieval tools for Qdrant
  - Create RAG agent with instructions

**Sequential Work** (depends on both tracks):
- API endpoints (`/api/chat`, `/api/health`)
- Session management + rate limiting middleware
- Docker multi-stage build with uv
- Deploy to Render (free tier)

**Deliverables**:
- Working FastAPI backend on Render
- OpenAI Agents SDK integrated
- Session management functional
- Rate limiting enforced

---

### Phase 3: Content Indexing (Week 2-3)

**Dependencies**:
- ✅ Backend deployed (Phase 2)
- ✅ Qdrant connection working

**Parallel Work Opportunities**:
- **Track A (MDX Processing)**: Independent
  - Implement unified/remark MDX parser
  - Build chunking logic (400-500 tokens)
  - Extract metadata (chapter, section, headings)

- **Track B (Embedding Generation)**: Independent
  - OpenAI embeddings API integration
  - Batch embedding generation
  - Vector storage in Qdrant

**Sequential Work** (depends on both tracks):
- End-to-end indexing pipeline
- `/api/index` endpoint for manual trigger
- Render cron job setup (daily at 2 AM UTC)
- Index initial book content (~50-100 pages)

**Deliverables**:
- Full book content indexed in Qdrant
- Daily re-indexing automated
- Metadata properly attached to chunks

---

### Phase 4: Frontend Integration (Week 3-4)

**Dependencies**:
- ✅ Backend `/api/chat` endpoint working (Phase 2)
- ⚠️ Can start in parallel with Phase 3

**Parallel Work Opportunities**:
- **Track A (ChatKit Integration)**: Independent
  - Install @openai/chatkit-react (React 19.x compatible)
  - Setup ChatProvider wrapper
  - Implement FloatingButton component
  - Style with Docusaurus theme

- **Track B (Text Selection)**: Independent
  - Implement useTextSelection hook
  - Build SelectionMenu component (@floating-ui)
  - Handle mobile touch events
  - Test across browsers

**Sequential Work** (depends on both tracks):
- Integrate both components into Docusaurus theme
- Connect to backend `/api/chat` endpoint
- Handle session cookies
- Error handling + retry logic

**Deliverables**:
- ChatKit chatbot embedded in book
- Text selection context menu working
- Seamless Docusaurus theme integration

---

### Phase 5: Testing & Optimization (Week 4-5)

**Dependencies**: All phases complete

**Parallel Work Opportunities**:
- **Track A (Backend Testing)**:
  - Unit tests (pytest)
  - Integration tests (API endpoints)
  - Load testing (100+ concurrent users)

- **Track B (Frontend Testing)**:
  - Component tests (Jest + React Testing Library)
  - E2E tests (Playwright)
  - Browser compatibility testing

- **Track C (Performance)**:
  - Query response time optimization (<3s p95)
  - Embedding search tuning (<500ms)
  - Cold start mitigation (Render free tier)

**Sequential Work** (after testing):
- Bug fixes
- Performance improvements
- Documentation updates

**Deliverables**:
- Test coverage >80%
- All success criteria met (SC-001 through SC-010)
- Production-ready deployment

---

## Parallel Work Summary

**Maximum Parallelization** (3 concurrent tracks):
1. **Backend Team**: Phase 2 Track A + B → Phase 3
2. **Frontend Team**: Phase 4 (can start after Phase 2 Track A)
3. **Content Team**: Prepare book content for indexing (any time)

**Critical Path** (longest dependency chain):
Phase 0 Research → Phase 1 Contracts → Phase 2 Backend → Phase 3 Indexing → Phase 5 Testing

**Estimated Total Duration**: 4-5 weeks with 2-3 developers working in parallel

---

## Risk Mitigation

| Risk | Impact | Mitigation | Owner |
|------|--------|------------|-------|
| Render free tier cold starts (~60s) | High - affects SC-002 (<3s response) | Keep backend warm with periodic pings OR upgrade to paid tier ($7/mo) | Backend |
| OpenAI Agents SDK API changes | Medium | Pin SDK version in pyproject.toml, monitor changelog | Backend |
| ChatKit React 19.x compatibility | Medium | Test early, fallback to custom components if needed | Frontend |
| Qdrant free tier limit (100K vectors) | Low | Monitor usage, ~50K chunks expected (well within limit) | Backend |
| Book content exceeds embedding budget | Low | Estimate: $0.50 one-time + $0.01/mo (very low cost) | Content |

---

**Plan Status**: ✅ Phase 0 complete | ➡️ Ready for Phase 1 (Design & Contracts)
