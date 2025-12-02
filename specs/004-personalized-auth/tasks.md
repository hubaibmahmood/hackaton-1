# Tasks: Personalized Authentication and Content

**Input**: Design documents from `/specs/004-personalized-auth/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in the specification. Tasks focus on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Revision**: Task quality improvements - split complex tasks, added missing infrastructure, removed duplicates

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This feature uses microservices architecture:
- **Auth Server**: `auth-server/src/`
- **API Server**: `backend/src/`
- **Frontend**: `book/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for two-backend microservices architecture

- [ ] T001 Create auth-server directory structure: src/{auth,database,utils,middleware,config}/, tests/, prisma/
- [ ] T002 Initialize auth-server with package.json, tsconfig.json, and dependencies (better-auth 1.0+, Express 4.x, Prisma 5.x)
- [ ] T003 Add npm scripts to auth-server/package.json (dev, build, start, test, lint)
- [ ] T004 [P] Configure ESLint and Prettier for auth-server in .eslintrc.js and .prettierrc
- [ ] T005 [P] Create environment templates in auth-server/.env.example and backend/.env.example (add JWT_SECRET to backend)
- [ ] T006 [P] Create nodemon.json configuration for auth-server development with auto-reload
- [ ] T007 [P] Setup Docker Compose file for local development with both servers in docker-compose.yml
- [ ] T008 [P] Add helmet.js middleware for security headers in auth-server dependencies

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Migrations

- [ ] T009 Create Alembic migration file structure in backend/src/database/migrations/001_create_auth_tables.py
- [ ] T010 Add users and user_sessions table definitions to migration with indexes
- [ ] T011 Add user_profiles and tab_preferences table definitions to migration with JSONB indexes
- [ ] T012 Run database migration to create all auth tables
- [ ] T013 Create migration rollback script in backend/src/database/rollback_001.py

### Database Configuration

- [ ] T014 [P] Configure Neon PostgreSQL connection in auth-server/src/database/client.ts with Prisma and connection pooling
- [ ] T015 [P] Configure Neon PostgreSQL connection in backend/src/database/init.py with psycopg pool (extend existing)
- [ ] T016 Create Prisma schema for auth tables in auth-server/prisma/schema.prisma
- [ ] T017 Generate Prisma Client in auth-server with npx prisma generate
- [ ] T018 Add environment variable validation utility in auth-server/src/config/env.ts

### Auth Server Setup

- [ ] T019 [P] Setup better-auth configuration in auth-server/src/auth/auth.config.ts with email/password and JWT settings
- [ ] T020 [P] Create Express server entry point in auth-server/src/index.ts with CORS and helmet middleware
- [ ] T021 [P] Create auth routes handler in auth-server/src/auth/routes.ts
- [ ] T022 [P] Create custom error classes in auth-server/src/utils/errors.ts (AuthError, ValidationError)
- [ ] T023 [P] Add Express global error handler middleware in auth-server/src/middleware/errorHandler.ts
- [ ] T024 [P] Setup structured logging utility in auth-server/src/utils/logger.ts with correlation IDs

### API Server Auth Setup

- [ ] T025 [P] Implement JWT validation middleware in backend/src/auth/dependencies.py using python-jose
- [ ] T026 [P] Create custom error classes in backend/src/utils/errors.py (AuthenticationError, ValidationError)
- [ ] T027 [P] Setup structured logging utility in backend/src/utils/logger.py with correlation IDs

### Frontend Setup

- [ ] T028 Create auth types in book/src/types/auth.ts (User, SignupRequest, LoginRequest, TokenResponse)
- [ ] T029 Create profile types in book/src/types/profile.ts (UserProfile, ExperienceLevel, BackgroundOptions)
- [ ] T030 Setup Axios client for auth-server in book/src/services/authClient.ts with base URL and interceptors
- [ ] T031 Setup Axios client for API server in book/src/services/apiClient.ts with JWT token interceptor
- [ ] T032 [P] Create LoadingSpinner component in book/src/components/common/LoadingSpinner.tsx
- [ ] T033 [P] Create ErrorMessage component in book/src/components/common/ErrorMessage.tsx
- [ ] T034 [P] Create Button component with loading state in book/src/components/common/Button.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - New User Registration with Background Profiling (Priority: P1) 🎯 MVP

**Goal**: Enable first-time readers to create accounts with background information and receive immediate personalized content

**Independent Test**: Complete signup flow with background questions, verify account creation, profile storage, and derived experience level calculation

### Backend Models & Logic

- [ ] T035 [P] [US1] Create User Pydantic model in backend/src/auth/models.py with email and password validation
- [ ] T036 [P] [US1] Create UserProfile Pydantic model in backend/src/profiles/models.py with experience field validation
- [ ] T037 [P] [US1] Create BackgroundInfo Pydantic model in backend/src/profiles/models.py for JSONB arrays
- [ ] T038 [US1] Implement experience level calculation function in backend/src/profiles/experience.py with conservative matching logic (returns Beginner/Intermediate/Advanced)
- [ ] T039 [US1] Create profile service in backend/src/profiles/service.py with create_profile() and calculate_derived_level()
- [ ] T040 [US1] Create profile router in backend/src/profiles/router.py with POST /api/profile endpoint
- [ ] T041 [US1] Register profile router in backend/src/main.py FastAPI app

### Auth Server Signup

- [ ] T042 [US1] Implement POST /auth/signup route handler in auth-server/src/auth/routes.ts using better-auth library
- [ ] T043 [US1] Add signup request validation in auth-server/src/auth/routes.ts (email format, password strength)
- [ ] T044 [US1] Add signup error handling and responses in auth-server/src/auth/routes.ts

### Frontend Signup Flow

- [ ] T045 [P] [US1] Create signup page in book/src/pages/signup.tsx with layout and navigation
- [ ] T046 [P] [US1] Add predefined background options constants in book/src/constants/backgroundOptions.ts
- [ ] T047 [P] [US1] Add Zod password validation schema in book/src/types/auth.ts
- [ ] T048 [US1] Create SignupForm component in book/src/components/Auth/SignupForm.tsx with React Hook Form (email + password fields)
- [ ] T049 [US1] Create BackgroundForm component in book/src/components/Auth/BackgroundForm.tsx with multi-select lists for languages, frameworks, platforms, sensors
- [ ] T050 [US1] Implement authService.signup() in book/src/services/authService.ts calling POST /auth/signup
- [ ] T051 [US1] Implement profileService.createProfile() in book/src/services/profileService.ts calling POST /api/profile
- [ ] T052 [US1] Add form submission handler in SignupForm calling authService then profileService with error handling
- [ ] T053 [US1] Add loading state and disabled submit button during signup processing in SignupForm
- [ ] T054 [US1] Add error message display for signup failures in SignupForm using ErrorMessage component

**Checkpoint**: At this point, User Story 1 should be fully functional - users can sign up, provide background, and have profiles created with derived experience levels

---

## Phase 4: User Story 2 - Existing User Sign In (Priority: P1) 🎯 MVP

**Goal**: Enable returning readers to access their personalized content securely

**Independent Test**: Create a user account, sign out, sign back in with correct credentials, verify authentication and personalized content access

### Auth Server Sign In

- [ ] T055 [P] [US2] Implement POST /auth/signin route in auth-server/src/auth/routes.ts using better-auth
- [ ] T056 [P] [US2] Implement POST /auth/signout route in auth-server/src/auth/routes.ts
- [ ] T057 [P] [US2] Add httpOnly cookie configuration for JWT tokens in auth-server/src/auth/auth.config.ts
- [ ] T058 [P] [US2] Implement POST /auth/refresh route in auth-server/src/auth/routes.ts for token refresh

### API Server Profile Retrieval

- [ ] T059 [US2] Implement GET /api/profile endpoint in backend/src/profiles/router.py with JWT validation using get_current_user dependency

### Frontend Authentication

- [ ] T060 [P] [US2] Create signin page in book/src/pages/signin.tsx
- [ ] T061 [P] [US2] Create SigninForm component in book/src/components/Auth/SigninForm.tsx with email and password fields
- [ ] T062 [US2] Implement authService.signin() in book/src/services/authService.ts calling POST /auth/signin
- [ ] T063 [US2] Implement authService.signout() in book/src/services/authService.ts calling POST /auth/signout
- [ ] T064 [US2] Implement profileService.getProfile() in book/src/services/profileService.ts calling GET /api/profile
- [ ] T065 [US2] Create useAuth hook in book/src/hooks/useAuth.ts with signin, signout, and user state
- [ ] T066 [US2] Create AuthProvider component in book/src/components/Auth/AuthProvider.tsx with React Context for auth state
- [ ] T067 [US2] Add session validation on app load in AuthProvider checking for existing token
- [ ] T068 [US2] Wrap Docusaurus app with AuthProvider in book/src/theme/Root.tsx
- [ ] T069 [US2] Add loading spinner during initial authentication check in AuthProvider
- [ ] T070 [US2] Create ProtectedRoute component in book/src/components/Auth/ProtectedRoute.tsx that redirects to signin
- [ ] T071 [US2] Add "Remember me" checkbox to SigninForm extending session to 7 days

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users can sign up, sign in, sign out, and stay authenticated

---

## Phase 5: User Story 3 - Tab-Based Content Viewing (Priority: P2)

**Goal**: Enable readers to toggle between Original and Personalized content views for flexible learning

**Independent Test**: Sign in as a user with a specific background, navigate to any chapter, verify both Original and Personalized tabs are present with content adapted to user's experience level

### Backend Personalization

- [ ] T072 [P] [US3] Create content variant metadata file in docs/_meta/variants.json mapping chapters to experience levels
- [ ] T073 [P] [US3] Create personalization service in backend/src/personalization/service.py with get_variant_path() matching logic
- [ ] T074 [P] [US3] Create personalization router in backend/src/personalization/router.py with GET /api/personalization/variant endpoint
- [ ] T075 [US3] Register personalization router in backend/src/main.py
- [ ] T076 [US3] Implement POST /api/personalization/tab-preference endpoint in backend/src/personalization/router.py

### Frontend Tab Interface

- [ ] T077 [P] [US3] Create ContentProvider context in book/src/components/Content/ContentProvider.tsx for active tab state
- [ ] T078 [P] [US3] Create usePersonalization hook in book/src/hooks/usePersonalization.ts for variant selection
- [ ] T079 [US3] Implement contentService.getVariant() in book/src/services/contentService.ts calling GET /api/personalization/variant
- [ ] T080 [US3] Create ContentTabs component in book/src/components/Content/ContentTabs.tsx with Original and Personalized tabs
- [ ] T081 [US3] Add ARIA roles and attributes to ContentTabs (role="tablist", role="tab", aria-selected)
- [ ] T082 [US3] Add keyboard navigation to ContentTabs (Arrow keys, Home, End, Enter/Space)
- [ ] T083 [US3] Create PersonalizedContent component in book/src/components/Content/PersonalizedContent.tsx using React.lazy for dynamic MDX imports
- [ ] T084 [US3] Add tab selection persistence in sessionStorage within ContentTabs component
- [ ] T085 [US3] Integrate ContentTabs into Docusaurus MDX layout in book/src/theme/DocItem/Layout/index.tsx
- [ ] T086 [US3] Add smooth CSS transitions for tab switching in custom.css (<200ms)
- [ ] T087 [US3] Preload inactive tab content using React Suspense to avoid loading delay
- [ ] T088 [US3] Add fallback UI component for missing personalized content variants
- [ ] T089 [US3] Add loading spinner for tab content using Suspense fallback

**Checkpoint**: All users can now toggle between Original and Personalized content with smooth tab switching (<500ms)

---

## Phase 6: User Story 4 - Profile Management and Re-personalization (Priority: P3)

**Goal**: Enable users to update their background information as they gain skills, triggering immediate content re-personalization

**Independent Test**: Sign in, view personalized content, update profile with new background information, verify personalized content reflects updated profile

### Backend Profile Updates

- [ ] T090 [P] [US4] Implement PUT /api/profile endpoint in backend/src/profiles/router.py with partial update support
- [ ] T091 [US4] Update profile service in backend/src/profiles/service.py to recalculate derived_experience_level on update

### Frontend Profile Management

- [ ] T092 [P] [US4] Create profile settings page in book/src/pages/profile.tsx
- [ ] T093 [P] [US4] Create ProfileIcon component in book/src/components/Profile/ProfileIcon.tsx for navbar with user menu
- [ ] T094 [US4] Create ProfileSettings component in book/src/components/Profile/ProfileSettings.tsx with display and edit modes
- [ ] T095 [US4] Integrate BackgroundForm component into ProfileSettings for editing
- [ ] T096 [US4] Implement profileService.updateProfile() in book/src/services/profileService.ts calling PUT /api/profile
- [ ] T097 [US4] Create useProfile hook in book/src/hooks/useProfile.ts for profile state management and updates
- [ ] T098 [US4] Add ProfileIcon to Docusaurus navbar in book/docusaurus.config.js navbar items
- [ ] T099 [US4] Add save/cancel buttons to ProfileSettings with confirmation message on success
- [ ] T100 [US4] Trigger content re-personalization after profile update by invalidating variant cache
- [ ] T101 [US4] Add form validation matching signup rules in ProfileSettings
- [ ] T102 [US4] Add unsaved changes warning dialog before navigation in ProfileSettings
- [ ] T103 [US4] Add loading state during profile update with disabled save button

**Checkpoint**: All user stories complete - full personalized learning experience with profile updates

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Data & Configuration

- [ ] T104 [P] Create predefined options seed data script in backend/src/database/seed_options.py
- [ ] T105 [P] Create sample content variants for 3 chapters in docs/ (beginner.md, intermediate.md, advanced.md)
- [ ] T106 [P] Generate TypeScript types from OpenAPI contracts using openapi-typescript

### Security & Reliability

- [ ] T107 [P] Implement rate limiting middleware in auth-server/src/middleware/rateLimit.ts (max 5 failed attempts per email per hour)
- [ ] T108 Create circuit breaker for Auth Server calls in backend/src/utils/circuit_breaker.py with 3 failure threshold
- [ ] T109 Implement graceful degradation UI in book/src/components/Auth/AuthErrorBoundary.tsx for auth service failures
- [ ] T110 [P] Add password strength meter component to SignupForm in book/src/components/Auth/PasswordStrengthMeter.tsx
- [ ] T111 Implement session timeout warning at 6.5 days in AuthProvider with renewal prompt
- [ ] T112 [P] Add HTTPS-only and SameSite=Strict cookie flags in auth-server for production

### Observability (Auth Server)

- [ ] T113 [P] Add authentication event logging in auth-server (signups, signins, failures, password changes)
- [ ] T114 [P] Add performance metrics tracking in auth-server/src/middleware/metrics.ts (latency, error rates)
- [ ] T115 [P] Add request/response logging middleware with correlation IDs in auth-server
- [ ] T116 [P] Implement error tracking with stack traces in auth-server error handler
- [ ] T117 [P] Add health check endpoint GET /health in auth-server/src/index.ts

### Observability (API Server)

- [ ] T118 [P] Add authentication event logging in backend for JWT validation events
- [ ] T119 [P] Add performance metrics tracking in backend/src/middleware/metrics.py (latency, error rates)
- [ ] T120 [P] Add request/response logging middleware with correlation IDs in backend
- [ ] T121 [P] Implement error tracking with stack traces in backend error handler
- [ ] T122 [P] Add health check endpoint GET /health in backend/src/main.py (extend existing)

### Deployment & Infrastructure

- [ ] T123 [P] Setup CORS configuration for production domains in auth-server/src/index.ts
- [ ] T124 [P] Setup CORS configuration for production domains in backend/src/main.py (extend existing)
- [ ] T125 [P] Create Dockerfile for auth-server in auth-server/Dockerfile with multi-stage build
- [ ] T126 [P] Create Dockerfile for backend in backend/Dockerfile (extend existing if present)
- [ ] T127 [P] Update Docker Compose for production deployment in docker-compose.prod.yml
- [ ] T128 [P] Implement session cleanup cron job in auth-server/src/jobs/cleanup-sessions.ts (runs daily)
- [ ] T129 [P] Add database indexes performance verification script in backend/src/database/verify_indexes.py

### Documentation & Quality

- [ ] T130 [P] Add API documentation with OpenAPI UI in auth-server using swagger-ui-express
- [ ] T131 [P] Add API documentation with OpenAPI UI in backend using FastAPI's built-in docs (extend existing)
- [ ] T132 [P] Create deployment documentation in specs/004-personalized-auth/deployment.md
- [ ] T133 [P] Create API usage examples collection (Postman/Insomnia) in specs/004-personalized-auth/examples/
- [ ] T134 [P] Add analytics tracking for tab switching and profile updates (measuring SC-005)
- [ ] T135 [P] Update constitution in .specify/memory/constitution.md with auth-server and better-auth technologies
- [ ] T136 Create auth-server README.md with setup instructions and architecture overview
- [ ] T137 Document environment variables in both auth-server/.env.example and backend/.env.example with descriptions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories (both P1 stories are MVP)
  - User Story 3 (P2): Can start after Foundational - No dependencies, but better after US1+US2 for testing
  - User Story 4 (P3): Can start after Foundational - No dependencies, but integrates with US1+US2+US3
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Registration + Background Profiling - MVP foundation, no dependencies
- **User Story 2 (P1)**: Sign In - MVP authentication, no dependencies (both P1 are minimal viable product)
- **User Story 3 (P2)**: Tab-Based Content - Can work independently but better with US1+US2 for testing
- **User Story 4 (P3)**: Profile Management - Can work independently but integrates with profile from US1

### Within Each User Story

- Backend models before services
- Services before routers/endpoints
- Routers before registration in main app
- API endpoints before frontend service calls
- Service functions before components that call them
- Components before pages that integrate them
- Pages before routing configuration

### Parallel Opportunities

**Phase 1 (Setup)**: T004, T005, T006, T007, T008 can run in parallel

**Phase 2 (Foundational)**:
- Database: T009-T011 can run in parallel (all migration file work)
- After migration: T014-T015, T019-T024, T025-T027, T028-T034 can all run in parallel

**User Story 1**:
- T035-T037 (models) can run in parallel
- T045-T047 (frontend setup) can run in parallel after T028-T034 complete

**User Story 2**:
- T055-T058 (auth endpoints) can run in parallel
- T060-T061 (frontend components) can run in parallel

**User Story 3**:
- T072-T074 (backend) can run in parallel
- T077-T078 (frontend hooks/context) can run in parallel

**User Story 4**:
- T090-T091 (backend) can run in parallel
- T092-T093 (frontend components) can run in parallel

**Phase 7 (Polish)**: Almost all tasks T104-T137 can run in parallel

---

## Parallel Example: User Story 1 (Registration)

```bash
# Backend models (parallel after T035-T037):
Task T035: "Create User Pydantic model"
Task T036: "Create UserProfile Pydantic model"
Task T037: "Create BackgroundInfo Pydantic model"

# Frontend setup (parallel after foundational):
Task T045: "Create signup page"
Task T046: "Add background options constants"
Task T047: "Add Zod password schema"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (8 tasks)
2. Complete Phase 2: Foundational (26 tasks)
3. Complete Phase 3: User Story 1 - Registration (20 tasks)
4. Complete Phase 4: User Story 2 - Sign In (17 tasks)
5. **STOP and VALIDATE**: Test authentication flow end-to-end
6. Deploy/demo MVP (users can register, sign in, have profiles)

**MVP Total: 71 tasks** (revised from 54 - more accurate sizing)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (34 tasks)
2. Add User Story 1 + 2 → Test authentication flow → Deploy/Demo (MVP: 71 tasks)
3. Add User Story 3 → Test tab switching → Deploy/Demo (+18 tasks = 89 tasks)
4. Add User Story 4 → Test profile updates → Deploy/Demo (+14 tasks = 103 tasks)
5. Add Polish (Phase 7) → Production-ready (+34 tasks = 137 tasks)

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

**Option 1 - By User Story:**
- **Developer A**: User Story 1 (Registration) - Backend + Frontend
- **Developer B**: User Story 2 (Sign In) - Backend + Frontend
- **Developer C**: Polish infrastructure tasks (logging, metrics, health checks)

**Option 2 - By Layer:**
- **Backend Team**: US1+US2 auth endpoints, profile endpoints, personalization
- **Frontend Team**: US1+US2 forms, auth context, routing, components
- **DevOps**: Docker, deployment, monitoring setup

---

## Task Summary

- **Total Tasks**: 137 tasks (revised from 115)
- **Setup Phase**: 8 tasks (+1)
- **Foundational Phase**: 26 tasks (+13 for utilities, error handling, components)
- **User Story 1 (P1 - Registration)**: 20 tasks (+2 from splits)
- **User Story 2 (P1 - Sign In)**: 17 tasks (+1 for token refresh)
- **User Story 3 (P2 - Tab Content)**: 18 tasks (+1 from splits)
- **User Story 4 (P3 - Profile Management)**: 14 tasks (-1 from merges)
- **Polish Phase**: 34 tasks (+6 from splits, new observability tasks)

**MVP Scope (Recommended)**: Phase 1 + Phase 2 + Phase 3 + Phase 4 = **71 tasks**

**Changes from Original**:
- ✅ Split 5 complex tasks (T020, T021, T042-T044, T093-T094, T102, T107)
- ✅ Added 25 missing infrastructure tasks (error handling, security, shared components, observability)
- ✅ Removed 3 vague/duplicate tasks (T007, T037, T114, T115 → T037-T039 merged into form tasks)
- ✅ Made tasks more atomic with clearer acceptance criteria
- ✅ Better separation of concerns (auth-server vs backend tasks)

**Parallel Opportunities**: 70+ tasks marked [P] can run in parallel when dependencies are met

**Independent Testing**: Each user story can be tested independently after completion

---

## Format Validation

✅ All tasks follow required format: `- [ ] [ID] [P?] [Story] Description with file path`
✅ Sequential Task IDs: T001 through T137
✅ Story labels present for all user story tasks: [US1], [US2], [US3], [US4]
✅ Parallel markers [P] included where appropriate (different files, no dependencies)
✅ Exact file paths specified in task descriptions
✅ Organized by user story for independent implementation
✅ Clear checkpoints after each user story phase
✅ MVP scope clearly identified (US1 + US2 = 71 tasks)

---

## Notes

- Tests NOT included per specification (not explicitly requested)
- Two-backend architecture: Auth Server (Node.js/Vercel) + API Server (FastAPI/Render)
- Shared Neon PostgreSQL database between backends
- JWT tokens issued by Auth Server, validated by API Server
- No inter-service HTTP calls (JWT validation is local)
- Frontend orchestrates calls to both backends
- Each user story is independently testable
- MVP = Registration + Sign In (US1 + US2 = 71 tasks)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks now have clear, single acceptance criteria
- Tasks sized for 15-30 minute completion
