# Implementation Plan: Personalized Authentication and Content

**Branch**: `004-personalized-auth` | **Date**: 2025-12-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-personalized-auth/spec.md`

## Summary

Implement user authentication system with better-auth.com integration that enables personalized textbook content delivery. Users register with email/password and provide software/hardware background information (programming languages, frameworks, experience years, robotics platforms, sensors). The system calculates and caches a derived experience level (Beginner/Intermediate/Advanced) using conservative matching logic. Authenticated users can toggle between Original and Personalized content tabs, with personalized content selected from pre-generated chapter variants based on their cached experience level. Users can update their profile through a dedicated Settings page, triggering re-calculation of derived experience level and immediate content re-personalization.

**Technical Approach**: Add dedicated Node.js authentication server with better-auth.com for user signup/signin/session management (issues JWT tokens). Extend existing FastAPI backend for profile management, experience calculation, and content personalization (validates JWT tokens from auth server). Create React components in Docusaurus for signup/signin forms and profile management, implement tab-based content rendering with MDX-based content variants. Two-backend microservices architecture with shared PostgreSQL database.

## Technical Context

**Language/Version**:
- Auth Server (NEW): Node.js 20+ LTS, TypeScript 5.6.2
- API Server (existing): Python 3.12+
- Frontend: TypeScript 5.6.2, React 19.0, Node.js 20+

**Primary Dependencies**:
- **Auth Server** (NEW - Node.js/TypeScript):
  - better-auth 1.0+ (authentication library)
  - Express or Fastify 4.x (web framework)
  - Prisma 5.x or TypeORM (database ORM)
  - jsonwebtoken (JWT token generation)
  - bcrypt (password hashing)
  - @types/* (TypeScript definitions)
- **API Server** (existing - Python/FastAPI):
  - FastAPI 0.104+ (existing)
  - python-jose or PyJWT (NEW - JWT validation only)
  - psycopg 3.1+ (existing - Neon Postgres)
  - Pydantic 2.0+ (existing - data validation)
  - httpx (existing - for inter-service communication if needed)
- **Frontend**:
  - Docusaurus 3.9.2 (existing)
  - React 19.0 (existing)
  - @better-auth/react (NEW - client auth SDK)
  - React Hook Form (NEW - form validation)
  - Zod (NEW - client-side validation)
  - Axios (NEW - HTTP client with interceptors)

**Storage**:
- Neon Serverless Postgres (existing) - **SHARED between both backends**
  - New tables: users, user_profiles, user_sessions, tab_preferences
  - Auth Server: manages users, user_sessions tables
  - API Server: manages user_profiles, tab_preferences tables
  - Extends existing RAG chatbot database

**Testing**:
- Auth Server: Jest/Vitest, Supertest (NEW - Node.js testing)
- API Server: pytest, pytest-asyncio (existing)
- Frontend: Jest 30.2+, @testing-library/react (existing)
- Contract testing: OpenAPI validation (both backends)
- E2E: Playwright (NEW - for auth flows across both services)

**Target Platform**:
- Auth Server: Linux server (Docker), Node.js runtime, deployed to cloud (NEW)
- API Server: Linux server (Docker), Python runtime, deployed to cloud (existing infrastructure)
- Frontend: Static site (GitHub Pages), Docusaurus SSG
- Both backends behind reverse proxy (Nginx) or API Gateway

**Project Type**: Microservices web application (2 backends + frontend)

**Performance Goals**:
- Authentication: < 10 seconds signin to content (SC-002)
- Tab switching: < 500ms without page reload (SC-004, NFR-005)
- Profile updates: < 5 seconds to re-personalized content (SC-006, NFR-006)
- Session validation: < 100ms added latency (NFR-007)
- Concurrent users: 100+ without degradation (SC-010)

**Constraints**:
- Microservices latency: Network calls between Auth Server and API Server (minimize with JWT validation)
- better-auth.com is JavaScript-only: Requires dedicated Node.js auth server
- GitHub Pages limitations: static site only, no server-side rendering
- Session storage: client-side cookies/localStorage for 7-day duration
- Content storage: Pre-generated variants only (no runtime generation)
- Password requirements: 8+ chars with uppercase, lowercase, number (NFR-001)
- Deployment: Two backends require orchestration (Docker Compose or Kubernetes)

**Scale/Scope**:
- Expected users: 100+ concurrent, 1000+ registered initially
- Content variants: ~15-20 chapters × 3 experience levels = 45-60 variants
- User data: ~50 fields per profile (languages, frameworks, platforms, sensors)
- Forms: 2 auth forms (signup/signin), 1 profile settings page, 8-10 background questions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Alignment with Core Principles

✅ **VIII. AI/Spec-Driven Book Creation** (Primary)
- Feature follows Spec-Kit Plus SDD workflow
- All decisions documented in spec with clarifications
- Implementation plan follows structured template

✅ **IX. Embedded RAG Chatbot** (Integration)
- Authentication via separate Node.js server, API Server (FastAPI) validates JWT tokens
- Uses existing Neon Postgres database (shared between both backends)
- Chatbot remains neutral (no personalization) per clarification
- User data accessible for future chatbot personalization if needed

✅ **VI. Learning Outcomes Driven Content** (Enabler)
- Personalization supports adaptive learning based on user background
- Content variants aligned with experience levels
- Helps users progress from Beginner → Intermediate → Advanced

⚠️ **Complexity Justification Required**:
- Adding authentication increases system complexity
- Rationale: Essential for personalized learning experience, user progress tracking, and future features (analytics, saved progress)
- Alternative rejected: Anonymous usage only - insufficient for long-term learning engagement and content personalization

### Constitution Compliance Summary

| Principle | Status | Notes |
|-----------|--------|-------|
| I-V (Robotics Focus) | N/A | Feature is infrastructure for book delivery |
| VI (Learning Outcomes) | ✅ Aligned | Enables adaptive content delivery |
| VII (Capstone Project) | N/A | Does not affect capstone |
| VIII (SDD Process) | ✅ Compliant | Following Spec-Kit Plus workflow |
| IX (RAG Chatbot) | ✅ Integrated | Extends existing backend infrastructure |
| X (Content Quality) | ✅ Maintained | Does not modify academic content |

**Gate Status**: ✅ PASS - Feature aligns with constitution principles and justified complexity.

## Project Structure

### Documentation (this feature)

```text
specs/004-personalized-auth/
├── plan.md              # This file (/sp.plan output)
├── research.md          # Technology decisions and best practices
├── data-model.md        # Database schema and entities
├── quickstart.md        # Developer setup guide
├── contracts/           # API contracts and schemas
│   ├── auth-api.yaml    # Authentication endpoints (OpenAPI)
│   ├── profile-api.yaml # Profile management endpoints
│   └── schemas/         # Pydantic/TypeScript shared schemas
├── checklists/          # Validation checklists
│   └── requirements.md  # Spec quality checklist (existing)
└── tasks.md             # Phase 2 output (/sp.tasks - NOT created yet)
```

### Source Code (repository root)

```text
auth-server/                     # NEW - Node.js Authentication Server
├── src/
│   ├── index.ts                 # Server entry point
│   ├── auth/
│   │   ├── auth.config.ts       # better-auth configuration
│   │   ├── routes.ts            # Auth routes (signup, signin, signout)
│   │   ├── middleware.ts        # Auth middleware
│   │   └── jwt.service.ts       # JWT token generation/validation
│   ├── database/
│   │   ├── client.ts            # Prisma/TypeORM client
│   │   ├── migrations/          # Database migrations
│   │   └── models/
│   │       ├── user.model.ts    # User entity
│   │       └── session.model.ts # Session entity
│   ├── config/
│   │   └── env.ts               # Environment configuration
│   └── utils/
│       ├── logger.ts            # Logging utility
│       └── errors.ts            # Error handling
├── tests/
│   ├── auth.test.ts             # Auth endpoint tests
│   └── integration/             # Integration tests
├── package.json
├── tsconfig.json
├── .env.example
└── Dockerfile

backend/                         # EXISTING - FastAPI API Server
├── src/
│   ├── auth/                    # MODIFIED - JWT validation only (no signup/signin)
│   │   ├── __init__.py
│   │   ├── dependencies.py      # JWT validation middleware, get_current_user
│   │   └── models.py            # User Pydantic models (for validation)
│   ├── profiles/                # NEW - Profile management module
│   │   ├── __init__.py
│   │   ├── router.py            # Profile CRUD endpoints
│   │   ├── service.py           # Profile business logic
│   │   ├── experience.py        # Experience level calculation
│   │   └── models.py            # Profile, BackgroundInfo models
│   ├── personalization/         # NEW - Content personalization module
│   │   ├── __init__.py
│   │   ├── router.py            # Content variant selection
│   │   ├── service.py          # Variant matching logic
│   │   └── models.py           # ContentVariant models
│   ├── database/                # EXTEND - Add new tables
│   │   ├── models.py           # SQLAlchemy ORM models (add User, UserProfile, etc.)
│   │   ├── migrations/         # Alembic migrations
│   │   └── init.py             # Database initialization
│   ├── config.py                # EXTEND - Add JWT secret for token validation
│   └── main.py                  # EXTEND - Register new routers
└── tests/
    ├── auth/                    # MODIFIED - JWT validation tests only
    ├── profiles/                # NEW - Profile tests
    └── personalization/         # NEW - Personalization tests

book/
├── src/
│   ├── components/
│   │   ├── Auth/               # NEW - Authentication components
│   │   │   ├── SignupForm.tsx  # Signup with background questionnaire
│   │   │   ├── SigninForm.tsx  # Signin form
│   │   │   ├── AuthProvider.tsx # Auth context and state
│   │   │   └── ProtectedRoute.tsx # Route guard
│   │   ├── Profile/            # NEW - Profile management
│   │   │   ├── ProfileSettings.tsx # Profile editing page
│   │   │   ├── BackgroundForm.tsx  # Background questionnaire
│   │   │   └── ProfileIcon.tsx     # Nav profile icon/menu
│   │   ├── Content/            # NEW - Content personalization
│   │   │   ├── ContentTabs.tsx     # Original/Personalized tabs
│   │   │   ├── PersonalizedContent.tsx # Variant renderer
│   │   │   └── ContentProvider.tsx # Content state management
│   │   └── [existing components]
│   ├── pages/                  # EXTEND - Add auth pages
│   │   ├── signup.tsx          # NEW - Signup page
│   │   ├── signin.tsx          # NEW - Signin page
│   │   └── profile.tsx         # NEW - Profile settings page
│   ├── hooks/                  # NEW - Custom React hooks
│   │   ├── useAuth.ts          # Auth state and actions
│   │   ├── useProfile.ts       # Profile state and actions
│   │   └── usePersonalization.ts # Content variant selection
│   ├── services/               # NEW - API client services
│   │   ├── authService.ts      # Auth API calls → Auth Server (Node.js)
│   │   ├── profileService.ts   # Profile API calls → API Server (FastAPI)
│   │   ├── authClient.ts       # Axios instance for Auth Server
│   │   └── apiClient.ts        # Axios instance for API Server
│   ├── types/                  # NEW - TypeScript types
│   │   ├── auth.ts             # Auth-related types
│   │   ├── profile.ts          # Profile-related types
│   │   └── content.ts          # Content variant types
│   └── theme/                  # EXTEND - Add auth-specific styles
│       └── custom.css          # Auth forms, profile page styles
└── tests/
    ├── components/             # Component tests
    └── integration/            # E2E auth flow tests

docs/                           # EXTEND - Add content variants
├── [existing chapters]/
│   ├── index.md               # Original content
│   ├── beginner.md            # NEW - Beginner variant
│   ├── intermediate.md        # NEW - Intermediate variant
│   └── advanced.md            # NEW - Advanced variant
└── _meta/                     # NEW - Variant metadata
    └── variants.json          # Variant mappings and metadata
```

**Structure Decision**: Microservices architecture with two backends:
1. **Auth Server (Node.js/TypeScript)** - NEW: Handles authentication via better-auth.com (signup, signin, signout, session management). Issues JWT tokens. better-auth.com is JavaScript-only, requiring Node.js runtime.
2. **API Server (FastAPI/Python)** - EXISTING: Validates JWT tokens, handles profile management, experience calculation, content personalization, and RAG chatbot.
3. **Frontend (Docusaurus/React)** - EXISTING: Calls Auth Server for authentication, calls API Server for profiles/personalization.

**Database**: Shared PostgreSQL (Neon) between both backends. Auth Server manages `users` and `user_sessions` tables. API Server manages `user_profiles` and `tab_preferences` tables.

**Deployment**: Both backends deployed as separate Docker containers, coordinated via Docker Compose or Kubernetes. Reverse proxy (Nginx) routes requests:
- `/auth/*` → Auth Server (port 3000)
- `/api/*` → API Server (port 8000)
- `/` → Frontend (GitHub Pages)

### Request Flow Diagrams

**Signup Flow**:
```
User → Frontend → Auth Server (POST /auth/signup)
                       ↓
                  better-auth.com library
                       ↓
                  PostgreSQL (insert users table)
                       ↓
                  Generate JWT token
                       ↓
Frontend ← JWT token + user data
     ↓
Frontend → API Server (POST /api/profile with JWT)
                ↓
           Validate JWT (shared secret)
                ↓
           PostgreSQL (insert user_profiles table)
                ↓
Frontend ← Profile data with derived experience level
```

**Signin Flow**:
```
User → Frontend → Auth Server (POST /auth/signin)
                       ↓
                  better-auth.com library
                       ↓
                  PostgreSQL (query users + sessions tables)
                       ↓
                  Validate credentials + generate JWT
                       ↓
Frontend ← JWT token + user ID
     ↓
Frontend → API Server (GET /api/profile with JWT)
                ↓
           Validate JWT
                ↓
           PostgreSQL (query user_profiles table)
                ↓
Frontend ← Profile + derived experience level
```

**Profile Update Flow**:
```
User → Frontend → API Server (PUT /api/profile with JWT)
                       ↓
                  Validate JWT (no call to Auth Server)
                       ↓
                  Recalculate derived experience level
                       ↓
                  PostgreSQL (update user_profiles table)
                       ↓
Frontend ← Updated profile data
     ↓
Frontend refreshes personalized content variants
```

**Content Request Flow**:
```
User → Frontend → API Server (GET /api/personalization/variant?chapter=X with JWT)
                       ↓
                  Validate JWT
                       ↓
                  PostgreSQL (query user_profiles for derived_experience_level)
                       ↓
                  Match chapter + experience level → variant path
                       ↓
Frontend ← Variant metadata (path: docs/chapter-1/intermediate.md)
     ↓
Frontend dynamically imports MDX variant
```

**Key Design Decisions**:
- **JWT tokens**: Auth Server issues, API Server validates (shared secret, no inter-service calls)
- **Shared database**: Both services connect to same PostgreSQL instance
- **No inter-service HTTP calls**: Auth Server and API Server do not call each other (reduces latency)
- **Frontend orchestrates**: Frontend makes separate calls to each backend as needed

## Complexity Tracking

> Complexity added is justified by core feature requirements and constitution principles.

| Aspect | Complexity Added | Justification | Simpler Alternative Rejected |
|--------|------------------|---------------|------------------------------|
| Microservices Architecture (2 Backends) | Separate Node.js Auth Server + FastAPI API Server | better-auth.com is JavaScript-only, requires Node.js runtime. Enables requirement compliance (better-auth.com specified in spec). Allows existing FastAPI backend to remain unchanged for RAG chatbot. | Single FastAPI backend with custom auth - rejected because violates requirement to use better-auth.com |
| better-auth.com Integration | JavaScript library (Node.js) | Industry-standard authentication with built-in security, password hashing, session management. Specified in feature requirements. Reduces security risk vs. custom implementation. | Roll-your-own auth - rejected due to security complexity and requirement non-compliance |
| Derived Experience Level Caching | Additional database field + recalculation logic | Performance optimization: eliminates experience level calculation on every content request. Enables <500ms tab switching (NFR-005). | Calculate on-demand - rejected due to latency impact on user experience |
| Multi-select Background Forms | Complex form UI with predefined + custom options | Ensures data consistency for content matching while allowing flexibility. Prevents typo/normalization issues. | Free-form text fields - rejected due to data quality and matching reliability issues |
| Content Variant Pre-generation | ~45-60 MDX files (15-20 chapters × 3 levels) | Ensures fast content delivery (<500ms tab switching). Aligns with Docusaurus static site architecture. | Runtime content generation - rejected due to static site constraints and performance |
| Conservative Experience Matching | Additional business logic | Prevents overwhelming users with knowledge gaps. Supports educational mission of progressive learning. | Use highest level or random - rejected due to poor learning experience for users with mixed backgrounds |

All complexity additions support core functional requirements (FR-001 through FR-018) and success criteria (SC-001 through SC-010), and align with constitution principles VI (Learning Outcomes) and IX (RAG Chatbot integration).

## Phase 0: Research & Decisions

See [research.md](./research.md) for detailed technology research, decision rationale, and best practices.

**Key Research Topics**:
1. better-auth.com integration patterns for Python/FastAPI
2. better-auth.com JavaScript SDK for React/Docusaurus
3. Session management strategies (cookies vs. localStorage vs. sessionStorage)
4. Docusaurus content variant rendering with MDX
5. PostgreSQL schema design for user profiles with multi-valued fields
6. Experience level calculation algorithms (conservative matching)
7. Tab-based content UI patterns in React
8. Graceful degradation strategies for external service failures
9. Password strength validation (client + server)
10. Profile form UX patterns for multi-select lists

## Phase 1: Design & Contracts

**Artifacts**:
- [data-model.md](./data-model.md) - Database schema, entities, relationships
- [contracts/](./contracts/) - OpenAPI specs for auth and profile APIs
- [quickstart.md](./quickstart.md) - Developer setup and local development guide

**Key Design Decisions**:
1. **Database Schema**: 4 tables (users, user_profiles, user_sessions, tab_preferences)
2. **API Design**: RESTful endpoints for auth + profiles, JWT bearer authentication
3. **Frontend State**: React Context for auth state, SWR for profile data caching
4. **Content Routing**: Dynamic imports in Docusaurus for variant selection
5. **Experience Calculation**: Pure function, idempotent, stored in database

## Phase 2: Tasks

**Output**: tasks.md (generated by `/sp.tasks` command - not part of `/sp.plan`)

**Task Categories** (preview):
1. Backend: Auth endpoints, profile CRUD, personalization service
2. Frontend: Auth forms, profile page, content tabs, auth context
3. Database: Migrations, seed data, indexes
4. Integration: better-auth setup, API client, error handling
5. Testing: Unit tests, integration tests, E2E auth flows
6. Documentation: API docs, developer guide, deployment notes

## Next Steps

1. ✅ Review and approve this implementation plan
2. ⏭️ Run `/sp.tasks` to generate detailed task breakdown
3. ⏭️ Run `/sp.implement` to execute tasks with TDD workflow
4. ⏭️ Create ADRs for significant architectural decisions (e.g., better-auth choice, experience matching logic)

## References

- Feature Specification: [spec.md](./spec.md)
- Constitution: [.specify/memory/constitution.md](../../.specify/memory/constitution.md)
- Research: [research.md](./research.md) (Phase 0 output)
- Data Model: [data-model.md](./data-model.md) (Phase 1 output)
- API Contracts: [contracts/](./contracts/) (Phase 1 output)
- Quickstart Guide: [quickstart.md](./quickstart.md) (Phase 1 output)
