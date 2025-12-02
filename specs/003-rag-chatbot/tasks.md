# Tasks: Integrated RAG Chatbot

**Input**: Design documents from `/specs/003-rag-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md

**Tests**: Test tasks are included based on plan.md testing requirements (pytest for backend, Jest for frontend)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Changes from v1**: Resized for atomicity (15-30 min tasks), added 7 integration verification tasks, removed redundancy

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `book/src/`
- Backend uses Python 3.12 with uv package manager
- Frontend uses React 19.x with TypeScript

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 [P] Setup backend project with uv and dependencies: Run `uv init --package .` in backend/, create backend/.python-version (3.12), edit backend/pyproject.toml to add FastAPI 0.104+, openai, qdrant-client 1.7+, psycopg3, pydantic 2.x, create backend/src/ and backend/.env.example with OPENAI_API_KEY, QDRANT_URL, NEON_DB_URL
- [X] T002 [P] Setup frontend ChatBot dependencies and structure: Install @openai/chatkit-react, @floating-ui/react in book/package.json, create book/src/components/ChatBot/ directory structure, verify npm install succeeds
- [X] T003 [P] Setup backend Docker multi-stage build with uv in backend/Dockerfile
- [X] T004 Setup Render deployment config in render.yaml (web service + cron job for daily indexing)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Setup Neon Postgres connection in backend/src/database/postgres.py with asyncpg
- [X] T006 [P] Setup Qdrant client in backend/src/database/qdrant.py with vector collection config (1536 dimensions, COSINE distance)
- [X] T007 [P] Create Qdrant collection: Execute collection creation with 1536 dimensions, COSINE distance, verify test vector insert succeeds
- [X] T008 [P] Create session schema SQL in backend/src/database/migrations/001_create_sessions.sql (session_id UUID primary key, conversation_history JSONB, rate_limit_counter INTEGER, rate_limit_window_start TIMESTAMP, expires_at TIMESTAMP, created_at TIMESTAMP)
- [X] T009 Run database migrations and verify schema: Execute 001_create_sessions.sql against Neon Postgres, verify sessions table exists with `SELECT * FROM sessions LIMIT 1`
- [X] T010 [P] Implement config management in backend/src/config.py using Pydantic Settings (load OPENAI_API_KEY, QDRANT_URL, NEON_DB_URL from environment)
- [X] T011 Setup FastAPI app with health check: Create backend/src/main.py with app initialization and CORS middleware (allow frontend origin), add /health endpoint returning {"status": "ok"}, verify app runs and /health returns 200
- [X] T012 Register API routes in main.py: Import chat, index, health routers, mount with prefixes (/api/chat, /api/index, /health), verify all routes accessible
- [X] T013 [P] Setup OpenAI client initialization in backend/src/services/embedding_service.py (text-embedding-3-small)
- [X] T014 [P] Create error handling middleware in backend/src/api/middleware.py (friendly errors, maintain context, log errors)
- [X] T015 [P] Setup logging configuration in backend/src/config.py (structured logging with timestamps, log level from env)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - General Book Content Questions (Priority: P1) 🎯 MVP

**Goal**: Enable readers to ask questions about book content and receive accurate, cited answers using OpenAI Agents SDK + RAG

**Independent Test**: Ask "What is a ROS2 node?" and verify chatbot provides accurate answer with source citations from book content

### Implementation for User Story 1

#### Backend - Data Models

- [X] T016 [P] [US1] Create Query and Response models in backend/src/models/query.py (Query: question text, session_id, timestamp, page_context; Response: answer text, citations list, confidence score)
- [X] T017 [P] [US1] Create Citation and Session models: SourceCitation in backend/src/models/content.py (chapter, section, page_reference, excerpt_text, citation_url), UserSession in backend/src/models/session.py (session_id UUID, conversation_history list, rate_limit_counter, rate_limit_window_start, expires_at)

#### Backend - OpenAI Agents SDK Integration

- [X] T018 [US1] Define custom Qdrant retrieval tool in backend/src/agents/tools.py (search_book_content function: takes query string, generates embedding via OpenAI, searches Qdrant, returns relevant chunks with metadata)
- [X] T019 [US1] Create RAG agent with instructions in backend/src/agents/rag_agent.py (Agent with GPT-4 Turbo, register custom tools, system instructions: always cite sources with chapter/section, stay within book scope, acknowledge out-of-scope questions)
- [X] T020 [US1] Implement agent execution with tool handling in backend/src/agents/rag_agent.py (run agent with user query, handle custom tool calls to Qdrant, collect tool results, return final response with citations)
- [X] T021 [US1] Add streaming support to agent responses in backend/src/agents/rag_agent.py (stream agent output token-by-token, preserve citation metadata in stream)

#### Backend - Services

- [X] T022 [US1] Implement embedding generation in backend/src/services/embedding_service.py (OpenAI text-embedding-3-small API, batch processing for multiple texts, error handling for API failures)
- [X] T023 [US1] Implement session CRUD operations in backend/src/services/session_service.py (create_session: generate UUID, insert to Postgres; load_session: fetch by session_id; validate_session: check expiry)
- [X] T024 [US1] Implement conversation history persistence in backend/src/services/session_service.py (persist_message: append to conversation_history JSONB, retrieve_history: load full conversation for context)
- [X] T025 [US1] Implement rate limiting logic in backend/src/services/session_service.py (check_rate_limit: enforce 10 queries/min per session using window-based counter, reset window after 60 seconds, raise RateLimitExceeded error)
- [X] T026 [US1] Implement Qdrant search with similarity scoring in backend/src/services/retrieval_service.py (search_by_embedding: query Qdrant with embedding vector, apply similarity threshold 0.7, return top-5 results with scores)
- [X] T027 [US1] Enrich search results with metadata in backend/src/services/retrieval_service.py (extract chapter, section, citation_url from chunk payload, format as SourceCitation models, attach to search results)

#### Backend - API Endpoint

- [X] T028 [US1] Implement /api/chat POST endpoint in backend/src/api/chat.py (accept ChatRequest with question + session_id, load or create session, check rate limit, call RAG agent with conversation history context, return ChatResponse)
- [X] T029 [US1] Add streaming support to /api/chat endpoint (stream agent responses using Server-Sent Events, maintain session context during stream, handle client disconnects gracefully)
- [X] T030 [US1] Add validation and error handling to chat endpoint in backend/src/api/chat.py (Pydantic validation for request/response, catch OpenAI API errors with friendly message, graceful degradation: display error + retry button, maintain conversation context on error)

#### Frontend - ChatKit Integration

- [X] T031 [P] [US1] Create ChatProvider wrapper in book/src/components/ChatBot/ChatProvider.tsx (configure apiUrl pointing to /api/chat, model: gpt-4-turbo, enable streaming, manage session via cookies)
- [X] T032 [P] [US1] Create FloatingButton component in book/src/components/ChatBot/FloatingButton.tsx (always visible trigger button, positioned bottom-right, Docusaurus theme compatible, opens ChatBot on click)
- [X] T033 [US1] Create main ChatBot widget in book/src/components/ChatBot/ChatBot.tsx (use ChatMessages and ChatInput from @openai/chatkit-react, handle open/close state, display citations as clickable links)
- [X] T034 [US1] Implement API client in book/src/services/chatService.ts (fetch /api/chat with POST, handle streaming responses, credentials: 'include' for cookies, parse SSE stream)
- [X] T035 [US1] Add ChatBot styling in book/src/components/ChatBot/ChatBot.css (match Docusaurus theme colors, responsive design for mobile/desktop, style citation links distinctly)
- [X] T036 [US1] Integrate ChatBot into Docusaurus theme in book/docusaurus.config.ts (add ClientModule for ChatProvider, ensure ChatBot available on all pages)
- [X] T037 [US1] Export ChatBot components from book/src/components/ChatBot/index.ts (export FloatingButton, ChatProvider, ChatBot, types), verify components importable in Docusaurus pages
- [X] T038 [US1] Verify frontend-backend connectivity: Test CORS configuration with frontend origin, verify session cookies set correctly with HTTP-only flag, test /health endpoint from frontend, ensure no CORS errors in browser console

#### Content Indexing (enables RAG)

- [X] T039 [US1] Implement MDX parser with metadata extraction in backend/src/indexing/chunker.py (use unified/remark to parse MDX, extract frontmatter for part/chapter metadata, parse heading hierarchy for section tracking, attach metadata to each parsed section)
- [X] T040 [US1] Implement chunking logic in backend/src/indexing/chunker.py (chunk_text function: split by 400-500 tokens using tiktoken, add 10-15% overlap between chunks, preserve code blocks without splitting, maintain heading context in each chunk)
- [X] T041 [US1] Implement indexing pipeline orchestrator in backend/src/indexing/indexer.py (index_file function: read single MDX file, parse and chunk, generate embeddings, upload chunks to Qdrant with metadata, verify single file indexes successfully)
- [X] T042 [US1] Implement batch indexing for multiple files in backend/src/indexing/indexer.py (index_directory function: traverse book/docs/ recursively, process all .md/.mdx files, progress tracking, error handling per file, continue on individual failures)
- [X] T043 [US1] Create /api/index POST endpoint in backend/src/api/index.py (trigger manual indexing, accept directory path parameter, run indexing asynchronously using background task, return job ID)
- [X] T044 [US1] Index initial book content: Execute batch indexing on book/docs/ directory (~50-100 pages), verify completion without errors
- [X] T045 [US1] Validate indexed content in Qdrant: Query Qdrant for total chunk count (expect 50+), verify metadata present (chapter, section, citation_url), run sample search query for "ROS2" and verify results returned with correct metadata

#### Testing for User Story 1

- [X] T046 [P] [US1] Unit test for embedding service in backend/tests/unit/test_embedding_service.py (mock OpenAI API, verify embeddings have shape [1536], test batch processing, test error handling)
- [X] T047 [P] [US1] Unit test for session service in backend/tests/unit/test_session_service.py (test rate limiting with multiple requests, test session expiry validation, test conversation history persistence)
- [X] T048 [P] [US1] Unit test for OpenAI Agents in backend/tests/unit/test_agents.py (mock agent.run(), verify custom tool calls to Qdrant, verify citation extraction from tool results)
- [X] T049 [US1] Integration test for /api/chat in backend/tests/integration/test_api_endpoints.py (send chat request, verify 200 response, verify response format includes answer + citations, test rate limit enforcement with 11th request)
- [X] T050 [US1] E2E test for RAG flow in backend/tests/integration/test_rag_flow.py (ask known question from book content, verify answer accuracy, verify citations reference correct chapters, test out-of-scope question detection)
- [X] T051 [P] [US1] Frontend component test in book/tests/ChatBot.test.tsx (render FloatingButton, simulate click to open ChatBot, simulate message send, verify API call made)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can ask questions and get cited answers from book content

---

## Phase 4: User Story 2 - Text Selection Queries (Priority: P2)

**Goal**: Enable readers to select text and ask questions about the selection via context menu

**Independent Test**: Select a paragraph about LIDAR, ask "How does this compare to cameras?" and verify chatbot references the selection

### Implementation for User Story 2

#### Frontend - Text Selection

- [X] T052 [P] [US2] Create useTextSelection hook in book/src/hooks/useTextSelection.ts (Selection API: listen to selectionchange event, track selected text + range, handle empty selections, support mobile touch events)
- [X] T053 [P] [US2] Create SelectionMenu component in book/src/components/ChatBot/SelectionMenu.tsx (use @floating-ui/react for positioning near selection, show "Ask about selection" button, handle click to open ChatBot with selected text)
- [X] T054 [US2] Add mobile touch support in book/src/hooks/useTextSelection.ts (handle touchend/touchstart events for mobile text selection, detect long-press, show menu on touch selection)
- [X] T055 [US2] Integrate SelectionMenu with ChatBot in book/src/components/ChatBot/ChatBot.tsx (pass selected_text to ChatProvider, pre-fill ChatInput with selection context, display selected text in chat UI)

#### Backend - Selection Context Handling

- [X] T056 [US2] Extend Query model in backend/src/models/query.py (add optional selected_text field, add selection_metadata with location/range info)
- [X] T057 [US2] Update RAG agent instructions in backend/src/agents/rag_agent.py (handle selection context: when selected_text present, reference it explicitly in response, compare selection to retrieved book content)
- [X] T058 [US2] Modify /api/chat endpoint in backend/src/api/chat.py (accept optional selected_text parameter in ChatRequest, pass to agent as context, include in conversation history)

#### Testing for User Story 2

- [X] T059 [P] [US2] Unit test for useTextSelection hook in book/tests/hooks/useTextSelection.test.ts (mock Selection API, verify state updates on selectionchange, verify cleanup on unmount)
- [X] T060 [US2] Integration test for selection queries in backend/tests/integration/test_api_endpoints.py (send chat request with selected_text, verify response references the selection, verify selection stored in conversation history)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - general queries AND text selection queries

---

## Phase 5: User Story 3 - Contextual Learning Assistance (Priority: P3)

**Goal**: Provide intelligent navigation and prerequisite guidance based on current page context

**Independent Test**: From Chapter 3, ask "What are the prerequisites?" and verify chatbot suggests Chapters 1-2

### Implementation for User Story 3

#### Backend - Page Context Awareness

- [X] T061 [US3] Extend Query model in backend/src/models/query.py (add optional current_page_url field, add page_metadata with part/chapter/section info)
- [X] T062 [US3] Enhance chunk metadata in backend/src/indexing/chunker.py (add prerequisite_chapters list based on book structure from _category_.json, add next_topics list from subsequent chapters, include in chunk payload)
- [X] T063 [US3] Update RAG agent instructions in backend/src/agents/rag_agent.py (provide navigation guidance: when asked about prerequisites, reference chunk metadata for prerequisite_chapters; when asked "what's next", suggest next_topics)
- [X] T064 [US3] Modify /api/chat endpoint in backend/src/api/chat.py (accept optional current_page_url parameter in ChatRequest, parse URL to extract part/chapter/section, pass to agent as page context)

#### Frontend - Page Context Injection

- [X] T065 [US3] Add page context detection in book/src/services/chatService.ts (read current URL from window.location.pathname, parse to extract current part/chapter, include in chat requests)
- [X] T066 [US3] Update ChatProvider in book/src/components/ChatBot/ChatProvider.tsx (inject current_page_url automatically into all chat requests, display current page context in ChatBot header)

#### Testing for User Story 3

- [X] T067 [US3] Integration test for contextual queries in backend/tests/integration/test_api_endpoints.py (send request with current_page_url for Chapter 3, ask "What are prerequisites?", verify response recommends Chapters 1-2)

**Checkpoint**: All three user stories (general, selection, contextual) should work independently and together

---

## Phase 6: User Story 4 - Search and Discovery (Priority: P3)

**Goal**: Enable topic search with direct links to all relevant book sections

**Independent Test**: Ask "Where is obstacle avoidance discussed?" and verify chatbot lists all relevant sections with links

### Implementation for User Story 4

#### Backend - Location-Based Search

- [X] T068 [US4] Add query classification in backend/src/agents/rag_agent.py (detect search/discovery intent from patterns: "where is", "find", "show me all", vs Q&A intent, set search_mode flag)
- [X] T069 [US4] Enhance retrieval service for discovery queries in backend/src/services/retrieval_service.py (when search_mode=true, return top-10 results instead of top-5, group results by chapter, include all matching sections)
- [X] T070 [US4] Update RAG agent instructions for discovery responses in backend/src/agents/rag_agent.py (when search_mode=true, format response as list of locations with brief context, include citation links for each location)

#### Frontend - Link Rendering

- [X] T071 [US4] Update ChatBot styling for citation links in book/src/components/ChatBot/ChatBot.css (style citations as clickable buttons/chips, add hover effects, ensure mobile-friendly tap targets)
- [X] T072 [US4] Test link navigation in book environment (click citation link in ChatBot, verify navigation to correct book page with anchor to section, verify back button returns to ChatBot)

#### Testing for User Story 4

- [X] T073 [US4] Integration test for discovery queries in backend/tests/integration/test_rag_flow.py (ask "Where is obstacle avoidance discussed?", verify response lists multiple locations with chapter names, verify all citations are valid URLs)

**Checkpoint**: All four user stories complete - full chatbot functionality delivered

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Production readiness, optimization, and deployment

### Daily Indexing Automation

- [X] T074 Setup daily indexing cron job: Create backend/src/indexing/scheduler.py with main() entry point for cron, add cleanup logic for expired sessions (DELETE FROM sessions WHERE expires_at < NOW()), configure Render cron job in render.yaml (daily at 2 AM UTC, command: uv run python -m src.indexing.scheduler), verify test run succeeds

### Performance & Optimization

- [X] T075 [P] Optimize Qdrant query performance in backend/src/services/retrieval_service.py (tune similarity threshold to 0.75 for higher precision, adjust top-k based on query type, add result caching for common queries)
- [X] T076 [P] Add response caching in backend/src/api/chat.py (cache common questions using Redis or in-memory LRU cache, 24-hour TTL, reduce OpenAI API costs)
- [X] T077 Implement cold start mitigation in backend/src/main.py (add /health ping endpoint for Render keep-warm, or upgrade to $7/mo tier for always-on)
- [X] T078 [P] Optimize frontend bundle size in book/package.json (code splitting for ChatKit components using React.lazy, defer ChatBot loading until FloatingButton clicked)

### Security & Error Handling

- [X] T079 [P] Add input validation in backend/src/api/chat.py (sanitize user input: strip HTML, limit message length to 2000 chars, validate session_id format as UUID)
- [X] T080 [P] Implement out-of-scope detection in backend/src/agents/rag_agent.py (detect questions outside book content: no relevant chunks found, low similarity scores; return friendly message: "This question is outside the book's scope. I can only answer questions about [book topics].")
- [X] T081 Add HTTPS enforcement in backend/src/main.py (secure cookies require HTTPS, redirect HTTP to HTTPS in production)
- [X] T082 [P] Add request logging in backend/src/api/middleware.py (log query text, session_id, response time, error types for analytics; ensure no PII logged)

### Documentation & Deployment

- [X] T083 [P] Create deployment guide in backend/README.md (Render setup: connect GitHub repo, set environment variables, configure build command with uv; document all env vars)
- [X] T084 [P] Create frontend integration guide in book/docs/chatbot-integration.md (how to customize ChatKit theme, configure colors, adjust positioning, disable on certain pages)
- [X] T085 [P] Update specs/003-rag-chatbot/quickstart.md with developer setup (install uv, run `uv sync`, setup local Qdrant with Docker, configure .env, run migrations, start FastAPI dev server)
- [ ] T086 Deploy backend to Render (connect GitHub repo, set environment variables: OPENAI_API_KEY, QDRANT_URL, NEON_DB_URL, configure build: `uv sync`, start: `uv run uvicorn src.main:app`, verify deployment succeeds)
- [ ] T087 Run production smoke tests: Verify /health endpoint responds 200, test sample chat query end-to-end from production frontend, verify Qdrant connectivity (search returns results), verify Neon connectivity (session created in DB), check response time <3s
- [ ] T088 Verify chatbot works on production Docusaurus site (deploy book to GitHub Pages, verify ChatBot FloatingButton appears on all pages, test sending message, verify no CORS errors, test on mobile device)

### Testing & Quality

- [X] T089 [P] Load testing for 100+ concurrent users in backend/tests/load/test_concurrent.py (use locust or similar, simulate 100 concurrent sessions, 10 queries/min per session, verify SC-007: no performance degradation)
- [X] T090 [P] Response time validation in backend/tests/performance/test_latency.py (measure p50, p95, p99 latency for chat endpoint, verify SC-002: p95 <3s under normal load)
- [X] T091 [P] Citation accuracy audit in backend/tests/audit/test_citations.py (test 50 sample questions, verify SC-003: 80%+ responses include citations, verify citations reference correct chapters)
- [ ] T092 Run full test suite: Execute `pytest backend/tests/ -v` for backend tests, execute `npm test` in book/ for frontend tests, verify all tests pass before merge

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1) can start after Foundational - No dependencies on other stories
  - User Story 2 (P2) can start after Foundational - Extends US1 but independently testable
  - User Story 3 (P3) can start after Foundational - Extends US1 but independently testable
  - User Story 4 (P3) can start after Foundational - Extends US1 but independently testable
- **Polish (Phase 7)**: Depends on at least US1 being complete (can start after MVP)

### User Story Dependencies

- **User Story 1 (P1)**: Foundation + Content Indexing → Can deliver standalone MVP
- **User Story 2 (P2)**: Requires US1 backend infrastructure but independent frontend feature
- **User Story 3 (P3)**: Requires US1 backend infrastructure, adds page context awareness
- **User Story 4 (P3)**: Requires US1 backend infrastructure, enhances retrieval service

### Within Each User Story

- Data models before services
- Services before API endpoints
- Backend endpoints before frontend integration
- Frontend components before integration with ChatBot
- Core implementation before tests
- Tests verify story works independently

### Parallel Opportunities

#### Phase 1 Setup (3 parallel tracks possible)
- T001 (backend setup) || T002 (frontend setup) || T003 (Docker)

#### Phase 2 Foundational (6 parallel tracks possible)
- T006+T007 (Qdrant) || T008+T009 (Postgres) || T010 (config) || T013 (OpenAI) || T014 (errors) || T015 (logging)

#### Phase 3 User Story 1 (multiple parallel opportunities)
- **Models** (2 parallel): T016 || T017
- **Agents** (2 parallel): T018 || T019
- **Frontend Components** (2 parallel): T031 || T032
- **Content Indexing** (can parallelize T039, T040)
- **Tests** (5 parallel): T046 || T047 || T048 || T051

#### User Story Parallelization (if multiple developers)
- After Foundational completes:
  - Developer A: User Story 1 backend (T016-T030)
  - Developer B: User Story 1 frontend (T031-T038)
  - Developer C: User Story 1 indexing (T039-T045)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. **Week 1**: Complete Phase 1 (Setup) + Phase 2 (Foundational)
2. **Week 2-3**: Complete Phase 3 (User Story 1) - backend + frontend + indexing
3. **Week 3**: VALIDATE - Test US1 independently with real book content
4. **Week 3-4**: Polish critical items (T074-T082) and deploy MVP
5. **Result**: Working chatbot that answers book questions with citations

### Incremental Delivery (Recommended)

1. **Sprint 1 (Week 1-3)**: Setup + Foundational + US1 → Deploy MVP ✅
2. **Sprint 2 (Week 4)**: Add US2 (text selection) → Deploy with selection feature ✅
3. **Sprint 3 (Week 5)**: Add US3 + US4 (contextual + search) → Full feature set ✅
4. **Sprint 4 (Week 6)**: Polish + optimization → Production ready ✅

Each sprint delivers working, testable increment without breaking previous functionality.

### Parallel Team Strategy (3 developers)

**Week 1**: All developers work together on Setup + Foundational

**Week 2-3** (after Foundational completes):
- **Developer A (Backend)**: T016-T030 (US1 backend: models, agents, services, API)
- **Developer B (Frontend)**: T031-T038 (US1 frontend: ChatKit integration)
- **Developer C (Indexing)**: T039-T045 (US1 content indexing pipeline)

**Week 4**: All test and integrate US1, then split again:
- **Developer A**: User Story 2 backend (T056-T058)
- **Developer B**: User Story 2 frontend (T052-T055)
- **Developer C**: Polish & optimization (T074-T078)

---

## Success Criteria Validation

Each user story maps to success criteria from spec.md:

- **US1 validates**: SC-001 (90% accuracy), SC-002 (<3s response), SC-003 (80% citations), SC-004 (85% out-of-scope detection), SC-006 (85% context maintained)
- **US2 validates**: SC-005 (95% selection context incorporated), SC-010 (handle 1 word to 5+ paragraphs)
- **US3 validates**: SC-006 (contextual responses), helps with SC-009 (reduce external searches)
- **US4 validates**: SC-009 (reduce external searches by 40%), helps with SC-008 (75% satisfaction)
- **Polish validates**: SC-007 (100 concurrent users), SC-002 (performance)

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability (US1, US2, US3, US4)
- Each user story should be independently completable and testable
- Stop at any checkpoint to validate story independently
- Backend uses Python 3.12 + uv package manager (initialize with `uv init --package .`)
- Frontend uses React 19.x + OpenAI ChatKit SDK
- Commit after each task or logical group (recommended: commit every 2-3 related tasks)
- All file paths are explicitly specified for autonomous execution
- Tasks sized for 15-30 minutes each for predictable estimation
- 7 integration verification tasks added (T007, T009, T012, T037, T038, T045, T087) to catch issues early
