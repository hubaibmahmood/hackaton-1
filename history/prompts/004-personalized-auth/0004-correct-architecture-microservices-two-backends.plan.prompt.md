---
id: 0004
title: correct-architecture-microservices-two-backends
stage: plan
date: 2025-12-02
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-personalized-auth
branch: 004-personalized-auth
user: hubaib
command: correction
labels: ["architecture-correction", "microservices", "better-auth-javascript-only", "dual-backend", "deployment-strategy"]
links:
  spec: ../spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-personalized-auth/plan.md
  - specs/004-personalized-auth/research.md
  - specs/004-personalized-auth/data-model.md
  - specs/004-personalized-auth/contracts/auth-api.yaml
  - specs/004-personalized-auth/contracts/profile-api.yaml
  - specs/004-personalized-auth/quickstart.md
  - CLAUDE.md
tests:
  - N/A - planning correction (no implementation yet)
---

## Prompt

User identified critical architectural error: "In plan.md it says 'Extend existing FastAPI backend with better-auth integration for authentication' But better auth is in javascript not python. how is it going to add better auth in fastapi backend?"

User also asked: "I have my fastAPI backend deployed on render free tier, this new node js backend can be deplyoed on another platform?"

User chose: **Option 2 - Add Node.js Auth Microservice with better-auth.com** (keeping requirement compliance)

User requested: Update ALL remaining documents with Render + Vercel cross-platform deployment strategy

## Response snapshot

**Critical Discovery**: better-auth.com is a **JavaScript/TypeScript library** (NOT an HTTP service) - requires Node.js runtime. Original plan incorrectly assumed FastAPI could integrate it directly.

**Architecture Correction**: Changed from single FastAPI backend to **microservices architecture with two backends**:

### New Architecture

```
┌────────────────────────────────────────────────────────┐
│              Frontend (GitHub Pages)                    │
│          Calls both backends independently              │
└───────────────┬────────────────┬───────────────────────┘
                │                │
    ┌───────────▼─────┐   ┌──────▼────────────┐
    │  Auth Server    │   │   API Server      │
    │  (Node.js)      │   │   (FastAPI)       │
    │                 │   │                   │
    │  better-auth    │   │  JWT Validation   │
    │  JWT Generation │   │  Profile Mgmt     │
    │  Session Mgmt   │   │  Personalization  │
    │  Port: 3000     │   │  RAG Chatbot      │
    │  Vercel         │   │  Port: 8000       │
    │                 │   │  Render (existing)│
    └────────┬────────┘   └─────┬─────────────┘
             │                  │
             └────────┬─────────┘
                      ▼
           ┌────────────────────┐
           │ Neon PostgreSQL    │
           │ (Shared Database)  │
           │                    │
           │ Auth Server owns:  │
           │ - users            │
           │ - user_sessions    │
           │                    │
           │ API Server owns:   │
           │ - user_profiles    │
           │ - tab_preferences  │
           └────────────────────┘
```

### Key Design Decisions

1. **Separate Node.js Auth Server**:
   - Required for better-auth.com (JavaScript-only library)
   - Handles: signup, signin, signout, session management
   - Issues JWT tokens with 7-day expiration
   - Deployed on **Vercel** (free tier optimized for Node.js)

2. **Existing FastAPI API Server**:
   - Validates JWT tokens (shared secret - no Auth Server call)
   - Handles: profile CRUD, experience calculation, personalization
   - Retains existing RAG chatbot functionality
   - Stays on **Render** (already deployed)

3. **Shared Database (Neon PostgreSQL)**:
   - Auth Server manages: `users`, `user_sessions` tables
   - API Server manages: `user_profiles`, `tab_preferences` tables
   - Single source of truth, distributed ownership

4. **JWT as Bridge**:
   - Auth Server issues JWT tokens → Frontend sends to API Server
   - API Server validates JWT locally (shared `JWT_SECRET`)
   - **Zero inter-service HTTP calls** = minimal latency

5. **Cross-Platform Deployment**:
   - **Auth Server → Vercel**: Serverless Node.js, 100GB bandwidth/month free, instant cold starts
   - **API Server → Render**: Existing deployment, 750 hours/month free
   - **Maximizes free tier limits** across platforms

### Files Updated

**1. plan.md**:
- Added microservices architecture summary
- Updated Technical Context with Auth Server (Node.js) + API Server (Python) split
- Added Request Flow Diagrams (signup, signin, profile update, content request)
- Updated Complexity Tracking with microservices justification
- Updated Constitution Check to reflect dual-backend integration

**2. research.md**:
- Completely rewrote Section 1: better-auth.com integration
  - Clarified it's a JavaScript library (NOT HTTP service)
  - Showed Node.js/Express implementation with better-auth
  - Showed FastAPI JWT validation (no signup/signin)
- Added Section 11: Cross-Platform Deployment Strategy
  - Vercel vs Render platform comparison
  - Deployment configurations for both backends
  - Critical requirements (shared JWT_SECRET, shared DATABASE_URL, CORS)
  - Cost analysis ($0/month within free tiers)
  - Monitoring and health checks

**3. data-model.md**:
- Added "Architecture: Shared Database, Distributed Ownership" section
- Added table ownership model with microservices diagram
- Added communication pattern diagrams (signup flow, profile update flow)
- Marked each table with owner: 🟦 Auth Server or 🟩 API Server
- Clarified read-only cross-access (API Server reads `users` via JWT user_id)

**4. contracts/auth-api.yaml**:
- Updated title: "Auth Server API (better-auth.com)"
- Updated description to clarify Node.js/Vercel deployment
- Updated servers: `localhost:3000` and `https://auth-yourbook.vercel.app`
- Added architecture explanation in API description

**5. contracts/profile-api.yaml**:
- Updated title: "API Server (Profile & Personalization)"
- Updated description to clarify FastAPI/Render deployment
- Updated servers: `localhost:8000` and `https://api-yourbook.onrender.com`
- Added authentication note (validates JWT from Auth Server)

**6. quickstart.md** (complete rewrite):
- Added two-backend architecture overview with ASCII diagram
- Split environment setup: auth-server/.env + backend/.env + book/.env
- Added "Generate Shared JWT Secret" critical step
- Split backend setup into Auth Server (Node.js) + API Server (FastAPI) sections
- Added deployment guide for Vercel (Auth Server) + Render (API Server)
- Updated common issues with cross-platform troubleshooting
- Added dual-backend health check commands

**7. CLAUDE.md**:
- Updated Active Technologies to separate Auth Server and API Server entries
- Updated Recent Changes with microservices architecture summary

**8. PHR created** (this file):
- Documents architecture correction rationale
- Records all files modified
- Captures deployment strategy decision

### Justification for Complexity

**Why Two Backends?**
- **better-auth.com requirement**: JavaScript-only, cannot run in Python
- **Requirement compliance**: Spec specifies better-auth.com (cannot substitute)
- **Existing infrastructure**: Render backend already deployed with RAG chatbot
- **Free tier optimization**: Vercel for Node.js + Render for Python = separate bandwidth/hour limits

**Alternatives Rejected**:
- **Option 1** (FastAPI custom auth): Violates requirement to use better-auth.com
- **Option 3** (Replace with Node.js): Breaks existing RAG chatbot backend

**Mitigation Strategies**:
- Shared JWT secret eliminates inter-service calls (stateless validation)
- Shared database reduces data duplication
- Docker Compose/Kubernetes for local development orchestration
- Health check endpoints on both backends for monitoring

### Deployment Strategy Advantages

| Aspect | Vercel (Auth Server) | Render (API Server) | Benefit |
|--------|---------------------|---------------------|---------|
| Free Tier | 100GB bandwidth/month | 750 hours/month | **Separate limits** |
| Cold Start | ~0ms (serverless) | ~30s (spin down) | Auth always instant |
| Best For | Node.js/TypeScript | Python/FastAPI | Platform-optimized |
| Build Time | 1-2 min | 3-5 min | Faster iterations |
| Deployment | Git push auto-deploy | Git push auto-deploy | Both automated |

**Cost**: $0/month (within free tiers of both platforms)

**Estimated Usage**:
- Vercel: ~5GB/month (auth only) → 95GB headroom
- Render: ~720 hours/month (always-on) → 30 hours buffer
- Neon: ~500MB storage, 50 compute hours → plenty of headroom

## Outcome

- ✅ Impact: **Corrected major architectural error** - identified better-auth.com as JavaScript-only library requiring Node.js runtime. Redesigned as microservices architecture with two backends sharing single database. Updated 8 files (plan, research, data-model, 2 API contracts, quickstart, CLAUDE.md, PHR) to reflect dual-backend design. Added comprehensive cross-platform deployment strategy (Vercel + Render) maximizing free tier limits. Architecture now technically feasible and requirement-compliant.

- 🧪 Tests: N/A - planning correction (implementation in Phase 2)

- 📁 Files: 8 files updated (plan.md, research.md, data-model.md, auth-api.yaml, profile-api.yaml, quickstart.md, CLAUDE.md, this PHR)

- 🔁 Next prompts: /sp.tasks (generate task breakdown for microservices implementation), /sp.adr (document architectural decisions: better-auth choice, microservices split, deployment strategy)

- 🧠 Reflection: Critical catch by user prevented implementation of infeasible architecture. Original plan assumed better-auth.com was an HTTP service or had Python SDK - both incorrect. Microservices adds complexity but is **necessary** for requirement compliance (better-auth.com specified in spec). Dual-backend design maintains existing RAG chatbot on Render while adding Node.js auth on Vercel. Shared JWT secret eliminates inter-service HTTP calls (key performance optimization). Cross-platform deployment maximizes free tier limits (Vercel 100GB + Render 750h vs single platform). All complexity justified by requirement and existing infrastructure constraints.

## Evaluation notes (flywheel)

- Failure modes observed: **Original plan assumed wrong technology constraints** - better-auth.com is JavaScript library, not HTTP service or Python-compatible. This would have caused implementation failure.
- Graders run and results (PASS/FAIL): Architecture Feasibility - FAIL → PASS (after correction), Requirement Compliance - PASS (better-auth.com retained), Deployment Strategy - PASS (Vercel + Render documented)
- Prompt variant (if applicable): architecture-correction-v1
- Next experiment (smallest change to try): During implementation, validate if better-auth.com can be configured to work with Prisma ORM on Neon PostgreSQL or if custom PostgreSQL adapter is needed. Also test if Vercel serverless functions handle better-auth session management correctly (7-day duration requirement).
