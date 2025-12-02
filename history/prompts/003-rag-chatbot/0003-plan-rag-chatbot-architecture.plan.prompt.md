---
id: 0003
title: plan rag chatbot architecture
stage: plan
date: 2025-12-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-rag-chatbot
branch: 003-rag-chatbot
user: hubaib
command: /sp.plan
labels: ["planning", "architecture", "rag", "chatbot", "research", "technical-decisions"]
links:
  spec: specs/003-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-rag-chatbot/plan.md
  - specs/003-rag-chatbot/research.md
tests:
  - none - planning stage
---

## Prompt

/sp.plan

(User initiated architectural planning workflow for RAG chatbot feature)

## Response snapshot

Completed Phase 0 architectural planning with comprehensive research and technical decision-making:

**Plan Structure Created** (`plan.md`):
- Summary: RAG chatbot for Docusaurus book using OpenAI Agents SDK + ChatKit SDK + FastAPI + Qdrant + Neon Postgres
- Technical Context: Python 3.12 with uv package manager, React 19.x, TypeScript 5.x, web application architecture
- Performance Goals: <3s p95 response, 100+ concurrent users, 10 req/min rate limit
- Scale/Scope: 50-100 pages, 100-999 concurrent readers, 10K-50K vector embeddings
- Project Structure: backend/ (FastAPI + agents/), book/ (Docusaurus React 19.x), scripts/ (indexing)

**Constitution Check** (✅ All Passed):
- ✅ Principle IX: Embedded RAG Chatbot - Direct implementation with specified tech stack
- ✅ Principle VI: Learning Outcomes - Enhances learning through interactive Q&A
- ✅ Principle VIII: Spec-Driven Development - Follows SDD workflow
- ✅ Principle X: Academic Integrity - Comprehensive safeguards implemented (85% out-of-scope detection, mandatory source citations, retrieval-first RAG architecture, daily content sync)

**Phase 0 Research Completed** (6 tasks via research agents):

1. **Deployment Platform → Render** (**UPDATED** per user requirements)
   - Free tier: 750 instance hours/month
   - Built-in cron support (Render Cron Jobs)
   - Docker support with Python 3.12
   - Cost: $0/month (free tier)
   - Trade-off: ~60s cold starts after 15min inactivity (acceptable for educational use)

2. **OpenAI Integration → OpenAI Agents SDK + ChatKit SDK** (**UPDATED** per user requirements)
   - Backend: OpenAI Agents SDK for RAG orchestration with custom Qdrant retrieval tools
   - Frontend: OpenAI ChatKit SDK (@openai/chatkit-react) for React 19.x
   - Official SDKs with production-ready features (streaming, tool calling, UI components)
   - Architecture: Frontend (ChatKit React 19.x) → FastAPI + Agents SDK (RAG + tools) → OpenAI GPT-4 Turbo (streaming)

3. **MDX Chunking → Hybrid Semantic + Section-Based**
   - Libraries: unified/remark ecosystem (@mdx-js/mdx, remark-mdx)
   - Strategy: Section-based (H2/H3 headers) + semantic chunking for long sections
   - Chunk size: 400-500 tokens (~1,600-2,000 chars)
   - Overlap: 10-15% (50-75 tokens)
   - Code handling: Include with metadata (educational context requires prose + code)

4. **Text Selection → Custom Hook + Floating UI**
   - Browser Selection API + @floating-ui/react
   - Custom `useTextSelection` hook
   - Lightweight, full control, no heavy dependencies
   - Mobile support via touchend/touchstart events

5. **Embeddings → OpenAI text-embedding-3-small**
   - Quality: 62.3% MTEB score (vs. 42.7% for open-source alternatives)
   - Cost: $0.02/1M tokens (~$0.50 one-time indexing, $0.01/mo queries)
   - No infrastructure needed (serverless)
   - 1536 dimensions, Qdrant-compatible

6. **Sessions → UUID + HTTP-only Cookies**
   - No PII, cryptographically secure
   - 24-hour expiry via cookie Max-Age
   - Rate limiting: 10 queries/min tracked in Postgres
   - Security: HTTP-only, Secure, SameSite=Lax

**Research Document** (`research.md`):
- Complete decision rationale with alternatives considered
- Implementation patterns and code examples
- Cost analysis and performance benchmarks
- 40+ source references

**Next Phase**: Phase 1 Design & Contracts (data-model.md, contracts/, quickstart.md)

## Outcome

- ✅ Impact: Comprehensive architectural plan with 6 major technical decisions researched and documented; **FINAL STACK**: Render (free tier), OpenAI Agents SDK (backend), OpenAI ChatKit SDK (frontend React 19.x), Python 3.12 + uv package manager, hybrid MDX chunking, custom text selection, OpenAI embeddings, UUID sessions. Architecture updated per user requirements to use official OpenAI SDKs and latest stable versions (Python 3.12, React 19.x).
- 🧪 Tests: none - planning stage
- 📁 Files: 2 files created and iteratively updated (plan.md, research.md) with user-requested architectural changes
- 🔁 Next prompts: Phase 1 design artifacts (data-model.md, contracts/, quickstart.md), then /sp.tasks for implementation tasks
- 🧠 Reflection: All 6 research tasks completed with clear decisions and rationale. Architecture optimized for educational use case (free tier compatibility, official SDKs, modern stack). User corrections integrated: (1) Python 3.12 + uv, (2) React 19.x, (3) Render deployment, (4) OpenAI Agents/ChatKit SDKs. Constitution compliance validated. Ready to proceed with detailed design and API contracts.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all principles satisfied)
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): none
