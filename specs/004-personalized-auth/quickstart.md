# Quickstart Guide: Personalized Authentication (Microservices)

**Feature**: 004-personalized-auth | **Branch**: `004-personalized-auth` | **Date**: 2025-12-02

This guide helps developers set up the **two-backend microservices architecture** locally for development and testing.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture Overview](#architecture-overview)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Auth Server Setup (Node.js)](#auth-server-setup-nodejs)
- [API Server Setup (FastAPI)](#api-server-setup-fastapi)
- [Frontend Setup](#frontend-setup)
- [Testing Authentication Flows](#testing-authentication-flows)
- [Deployment Guide](#deployment-guide)
- [Common Issues](#common-issues)
- [Next Steps](#next-steps)

## Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| **Node.js** | 20+ LTS | Auth Server runtime + Frontend build |
| **Python** | 3.12+ | API Server runtime |
| **PostgreSQL** | 15+ | Shared database (or Neon Serverless) |
| **Git** | 2.x | Version control |
| **npm** | 10+ | Node.js package manager |
| **pip** | 24+ | Python package manager |

### Optional Tools

- **Docker** (for containerized PostgreSQL)
- **Postman** or **curl** (for API testing)
- **pgAdmin** or **psql** (for database inspection)
- **Vercel CLI** (for Auth Server deployment)

### Verify Installation

```bash
# Check Node.js version
node --version   # Should be 20+
npm --version    # Should be 10+

# Check Python version
python --version  # Should be 3.12+
pip --version     # Should be 24+

# Check PostgreSQL
psql --version   # Should be 15+

# Check Git
git --version
```

## Architecture Overview

This feature uses a **microservices architecture** with **two independent backends** sharing a single database:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (GitHub Pages)                   │
│              https://username.github.io/book                 │
│                                                              │
│  Calls:                                                      │
│  - Auth Server for signup/signin/signout                    │
│  - API Server for profiles/personalization                  │
└────────────────┬────────────────────┬──────────────────────┘
                 │                    │
      ┌──────────▼────────┐    ┌─────▼──────────────────┐
      │  Auth Server      │    │  API Server            │
      │  (Node.js)        │    │  (FastAPI)             │
      │                   │    │                        │
      │  better-auth.com  │    │  JWT Validation        │
      │  JWT Generation   │    │  Profile Management    │
      │  Session Mgmt     │    │  Personalization       │
      │                   │    │  RAG Chatbot (existing)│
      │  Port: 3000       │    │  Port: 8000            │
      │  Platform: Vercel │    │  Platform: Render      │
      └──────────┬────────┘    └─────┬──────────────────┘
                 │                   │
                 └─────────┬─────────┘
                           ▼
                ┌─────────────────────┐
                │  Neon PostgreSQL    │
                │  (Shared Database)  │
                │                     │
                │  Auth Server owns:  │
                │  - users            │
                │  - user_sessions    │
                │                     │
                │  API Server owns:   │
                │  - user_profiles    │
                │  - tab_preferences  │
                └─────────────────────┘
```

### Why Two Backends?

**better-auth.com is a JavaScript library** (not an HTTP service) - it requires Node.js runtime. Since the existing RAG chatbot backend is Python/FastAPI on Render, we add a separate Node.js Auth Server for authentication.

**Key Design**: Auth Server issues JWT tokens → Frontend sends JWT to API Server → API Server validates JWT locally (shared secret) → **No inter-service HTTP calls** = minimal latency.

## Environment Setup

### 1. Clone Repository and Switch Branch

```bash
# Clone the repository
git clone <repository-url>
cd book-generation

# Switch to feature branch
git checkout 004-personalized-auth

# Verify you're on the correct branch
git branch --show-current  # Should show: 004-personalized-auth
```

### 2. Generate Shared JWT Secret

**CRITICAL**: Both backends MUST use the **same** JWT secret for token generation/validation.

```bash
# Generate strong 32-character secret
openssl rand -base64 32

# Output example: kX8mP2vZ9qR4nL7wH3jK6tY1sU5aF0bE

# Save this value - you'll use it in BOTH backend .env files
```

### 3. Create Environment Files

#### Auth Server `.env`

Create `auth-server/.env`:

```bash
# Database Configuration (Neon Serverless Postgres) - SAME as API Server
DATABASE_URL=postgresql://username:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

# JWT Configuration - MUST MATCH API Server
JWT_SECRET=kX8mP2vZ9qR4nL7wH3jK6tY1sU5aF0bE
JWT_ALGORITHM=HS256
JWT_EXPIRATION=7d

# better-auth Configuration
BETTER_AUTH_SECRET=your-better-auth-secret-key-different-from-jwt
BETTER_AUTH_BASE_URL=http://localhost:3000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://username.github.io

# Environment
NODE_ENV=development

# Server Port
PORT=3000
```

#### API Server `.env`

Create `backend/.env`:

```bash
# Database Configuration (Neon Serverless Postgres) - SAME as Auth Server
DATABASE_URL=postgresql://username:password@ep-cool-darkness-123456.us-east-2.aws.neon.tech/neondb?sslmode=require

# JWT Configuration - MUST MATCH Auth Server
JWT_SECRET=kX8mP2vZ9qR4nL7wH3jK6tY1sU5aF0bE
JWT_ALGORITHM=HS256

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,https://username.github.io

# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
```

#### Frontend `.env`

Create `book/.env.local`:

```bash
# Backend API URLs
REACT_APP_AUTH_SERVER_URL=http://localhost:3000
REACT_APP_API_SERVER_URL=http://localhost:8000/api/v1

# Environment
NODE_ENV=development
```

### 4. Get Neon PostgreSQL Connection String

1. **Create Neon Account**: [neon.tech](https://neon.tech/)
2. **Create Database**: Use existing project or create new
3. **Copy Connection String**:
   ```
   postgresql://username:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```
4. **Update `.env` files**: Paste connection string into `DATABASE_URL` in **both** auth-server/.env and backend/.env

## Database Setup

### Shared Database Strategy

Both Auth Server and API Server connect to the **same Neon PostgreSQL database** but manage different tables:

| Backend | Tables Managed | Operations |
|---------|---------------|------------|
| **Auth Server** | `users`, `user_sessions` | Signup, signin, session CRUD |
| **API Server** | `user_profiles`, `tab_preferences` | Profile CRUD, personalization |

### Run Database Migrations

#### For Auth Server (Prisma)

```bash
cd auth-server

# Install dependencies (includes Prisma)
npm install

# Generate Prisma client from schema
npx prisma generate

# Push schema to database (creates users, user_sessions tables)
npx prisma db push

# Verify tables created
npx prisma studio  # Opens browser UI to inspect database
```

#### For API Server (Alembic)

```bash
cd backend

# Install dependencies (includes Alembic)
pip install -r requirements.txt

# Create migration for user_profiles, tab_preferences
alembic revision --autogenerate -m "Add profile and preferences tables"

# Apply migrations
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: users, user_sessions, user_profiles, tab_preferences
```

### Seed Development Data (Optional)

```bash
# Seed predefined options for profile forms
cd backend
python scripts/seed_profile_options.py

# Verify seed data
psql $DATABASE_URL -c "SELECT * FROM profile_options LIMIT 5;"
```

## Auth Server Setup (Node.js)

### 1. Install Dependencies

```bash
cd auth-server

# Install Node.js dependencies
npm install

# Key packages installed:
# - better-auth: Authentication library
# - express: Web framework
# - prisma: Database ORM
# - @prisma/client: Prisma client
# - cors: CORS middleware
# - dotenv: Environment variables
```

### 2. Configure better-auth

The better-auth configuration is in `auth-server/src/auth/auth.config.ts`:

```typescript
// auth-server/src/auth/auth.config.ts
import { betterAuth } from "better-auth";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

export const auth = betterAuth({
  database: prisma,
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set true in production
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Refresh daily
  },
  jwt: {
    secret: process.env.JWT_SECRET!,
    expiresIn: "7d",
  },
});
```

### 3. Run Auth Server

```bash
# Development mode (hot reload with tsx)
npm run dev

# Or using Node directly
npm start

# Server will start at http://localhost:3000
```

### 4. Verify Auth Server is Running

```bash
# Check health endpoint
curl http://localhost:3000/health

# Expected response:
# {"status":"healthy","service":"auth-server","timestamp":"2025-12-02T..."}

# Test signup endpoint
curl -X POST http://localhost:3000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# Expected: 201 Created with JWT token
```

## API Server Setup (FastAPI)

### 1. Install Python Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Key packages installed:
# - fastapi: Web framework
# - python-jose[cryptography]: JWT validation
# - psycopg[binary]: PostgreSQL driver
# - pydantic: Data validation
# - alembic: Database migrations
```

### 2. Configure JWT Validation

The JWT validation is in `backend/src/auth/dependencies.py`:

```python
# backend/src/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Validate JWT token issued by Auth Server"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.getenv("JWT_SECRET"),
            algorithms=[os.getenv("JWT_ALGORITHM", "HS256")]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return {"user_id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
```

### 3. Run API Server

```bash
# Development mode (hot reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m uvicorn src.main:app --reload

# Server will start at http://localhost:8000
```

### 4. Verify API Server is Running

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected"}

# Check OpenAPI docs (interactive)
open http://localhost:8000/docs  # macOS
xdg-open http://localhost:8000/docs  # Linux

# Test profile endpoint (requires JWT from Auth Server)
# First, get JWT from signup/signin, then:
curl -X GET http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer <JWT_TOKEN_FROM_AUTH_SERVER>"
```

## Frontend Setup

### 1. Install Node.js Dependencies

```bash
cd book

# Install dependencies
npm install

# Key packages installed:
# - @better-auth/react: Auth client SDK
# - react-hook-form: Form validation
# - zod: Schema validation
# - axios: HTTP client
```

### 2. Configure API Clients

The frontend has two separate API clients:

```typescript
// book/src/services/authClient.ts
import axios from 'axios';

export const authClient = axios.create({
  baseURL: process.env.REACT_APP_AUTH_SERVER_URL, // http://localhost:3000
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// book/src/services/apiClient.ts
export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_SERVER_URL, // http://localhost:8000/api/v1
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to API client requests
apiClient.interceptors.request.use((config) => {
  // No need to manually add Authorization header from localStorage;
  // httpOnly cookie will be automatically sent by the browser for same-origin requests.
  // For cross-origin requests, ensure CORS 'withCredentials' is set to true and 
  // backend handles cookie-based authentication.
  return config;
});
```

### 3. Run Development Server

```bash
# Start Docusaurus dev server
npm start

# Or explicitly specify port
npm start -- --port 3000

# Server will start at http://localhost:3000
```

### 4. Verify Frontend is Running

1. Open browser: http://localhost:3000
2. Navigate to signup page: http://localhost:3000/signup
3. Check browser console for errors
4. Verify both backends are accessible:
   - Auth Server: http://localhost:3000 (Node.js)
   - API Server: http://localhost:8000 (FastAPI)

## Testing Authentication Flows

### End-to-End Signup Flow

```bash
# Terminal 1: Start Auth Server
cd auth-server && npm run dev

# Terminal 2: Start API Server
cd backend && uvicorn src.main:app --reload

# Terminal 3: Start Frontend
cd book && npm start

# Browser: Navigate to http://localhost:3000/signup
```

**Signup Steps**:
1. Fill email: `test@example.com`
2. Fill password: `TestPass123` (meets requirements)
3. Select programming languages: Python, C++
4. Enter software experience: 3 years
5. Select robotics platforms: Arduino
6. Enter hardware experience: 2 years
7. Click "Sign Up"

**Expected Flow**:
```
1. Frontend → Auth Server: POST /auth/signup {email, password}
2. Auth Server: Insert into users table
3. Auth Server → Frontend: JWT token
4. Frontend → API Server: POST /api/profile {background} + JWT
5. API Server: Validate JWT, insert into user_profiles
6. API Server → Frontend: Profile with derived_experience_level="Intermediate"
7. Frontend: Redirect to home with personalized content
```

### Manual API Testing

#### Test Auth Server

```bash
# 1. Signup
curl -X POST http://localhost:3000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manual@test.com",
    "password": "ManualTest123"
  }'

# Save JWT token from response

# 2. Signin
curl -X POST http://localhost:3000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manual@test.com",
    "password": "ManualTest123"
  }'

# 3. Get current user
curl -X GET http://localhost:3000/auth/me \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

#### Test API Server

```bash
# 1. Create profile (after getting JWT from Auth Server)
curl -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "programmingLanguages": ["Python", "C++"],
    "frameworks": ["ROS 2"],
    "softwareExperienceYears": 4,
    "roboticsPlatforms": ["Custom Robot"],
    "sensorsActuators": ["LiDAR", "IMU"],
    "hardwareExperienceYears": 3
  }'

# 2. Get profile
curl -X GET http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer <JWT_TOKEN>"

# 3. Update profile
curl -X PUT http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "programmingLanguages": ["Python", "C++", "Rust"],
    "softwareExperienceYears": 6
  }'
```

### Automated E2E Tests

```bash
# Install Playwright
npm install --save-dev @playwright/test

# Run E2E tests
npx playwright test

# Run specific test suite
npx playwright test tests/e2e/auth-flow.spec.ts

# Run in headed mode (see browser)
npx playwright test --headed

# Debug mode
npx playwright test --debug
```

## Deployment Guide

### Deploy Auth Server to Vercel

**Prerequisites**:
- Vercel account (free tier)
- Vercel CLI installed: `npm install -g vercel`

**Steps**:
```bash
cd auth-server

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Set environment variables in Vercel Dashboard:
# - DATABASE_URL (same as Neon)
# - JWT_SECRET (same as API Server)
# - BETTER_AUTH_SECRET
# - CORS_ORIGINS=https://username.github.io
```

**Post-Deployment**:
- Note the deployment URL: `https://auth-yourbook.vercel.app`
- Update frontend `.env.production`:
  ```bash
  REACT_APP_AUTH_SERVER_URL=https://auth-yourbook.vercel.app
  ```

### Deploy API Server to Render

**Prerequisites**:
- Render account (free tier)
- Existing deployment (for RAG chatbot)

**Steps**:
1. Go to Render Dashboard
2. Select existing service or create new
3. Update environment variables:
   ```bash
   DATABASE_URL=<same-as-Neon>
   JWT_SECRET=<same-as-Auth-Server>
   CORS_ORIGINS=https://username.github.io
   ```
4. Deploy from `backend/` directory

**Post-Deployment**:
- Note the deployment URL: `https://api-yourbook.onrender.com`
- Update frontend `.env.production`:
  ```bash
  REACT_APP_API_SERVER_URL=https://api-yourbook.onrender.com/api/v1
  ```

### Deploy Frontend to GitHub Pages

```bash
cd book

# Build with production environment variables
REACT_APP_AUTH_SERVER_URL=https://auth-yourbook.vercel.app \
REACT_APP_API_SERVER_URL=https://api-yourbook.onrender.com/api/v1 \
npm run build

# Deploy to GitHub Pages (via GitHub Actions)
git add .
git commit -m "Deploy frontend with production URLs"
git push origin 004-personalized-auth

# Merge to main branch to trigger GitHub Pages deployment
```

### Verify Production Deployment

```bash
# 1. Check Auth Server health
curl https://auth-yourbook.vercel.app/health

# 2. Check API Server health
curl https://api-yourbook.onrender.com/health

# 3. Test signup flow in production
# Open: https://username.github.io/book/signup
```

## Common Issues

### Issue: Database Connection Failed

**Error**: `Connection refused` or `could not connect to server`

**Solutions**:
1. Verify both `.env` files have **identical** `DATABASE_URL`
2. Check Neon database is active (free tier doesn't sleep)
3. Test connection manually:
   ```bash
   psql $DATABASE_URL -c "SELECT 1;"
   ```
4. Verify connection string includes `?sslmode=require`

### Issue: JWT Token Mismatch

**Error**: `401 Unauthorized` or `Invalid token` from API Server

**Solutions**:
1. **CRITICAL**: Verify both backends use **identical** `JWT_SECRET`:
   ```bash
   # Auth Server
   cat auth-server/.env | grep JWT_SECRET

   # API Server
   cat backend/.env | grep JWT_SECRET

   # Must be EXACTLY the same
   ```
2. Restart both servers after changing JWT_SECRET
3. Clear browser localStorage and re-authenticate

### Issue: CORS Errors in Browser

**Error**: `Access blocked by CORS policy`

**Solutions**:
1. Verify `CORS_ORIGINS` in **both** backend `.env` files includes frontend URL:
   ```bash
   # Development
   CORS_ORIGINS=http://localhost:3000

   # Production
   CORS_ORIGINS=https://username.github.io
   ```
2. Restart both servers after changing CORS settings
3. Check browser console for specific origin being blocked

### Issue: Auth Server Not Found

**Error**: `Failed to fetch` or `ERR_CONNECTION_REFUSED` for Auth Server

**Solutions**:
1. Verify Auth Server is running on port 3000:
   ```bash
   lsof -i :3000  # Should show node process
   ```
2. Check frontend `.env.local` has correct URL:
   ```bash
   REACT_APP_AUTH_SERVER_URL=http://localhost:3000
   ```
3. Try accessing directly: `curl http://localhost:3000/health`

### Issue: API Server Returns 401 for Valid JWT

**Error**: API Server rejects JWT issued by Auth Server

**Solutions**:
1. Verify JWT_SECRET matches on both backends (see JWT Token Mismatch)
2. Check JWT hasn't expired (7-day default):
   ```bash
   # Decode JWT to check expiration
   echo "<JWT_TOKEN>" | cut -d'.' -f2 | base64 -d | jq
   ```
3. Verify Auth Server is actually issuing JWT in response
4. Check API Server logs for specific validation error

### Issue: Prisma Client Not Generated

**Error**: `Cannot find module '@prisma/client'`

**Solution**:
```bash
cd auth-server
npx prisma generate
npm run dev
```

### Issue: Alembic Migration Conflicts

**Error**: `Target database is not up to date`

**Solution**:
```bash
cd backend
alembic current  # Check current version
alembic history  # View migration history
alembic upgrade head  # Apply all pending migrations
```

### Issue: better-auth Configuration Error

**Error**: `better-auth setup failed` or module not found

**Solutions**:
1. Verify `better-auth` is installed:
   ```bash
   cd auth-server && npm list better-auth
   ```
2. Check `auth.config.ts` imports are correct
3. Verify Prisma client is generated: `npx prisma generate`
4. Restart Auth Server

### Issue: Vercel Deployment Failed

**Error**: Build or deployment failure on Vercel

**Solutions**:
1. Verify `vercel.json` exists in `auth-server/`
2. Check build command in Vercel dashboard:
   ```
   npm run build
   ```
3. Verify all environment variables set in Vercel dashboard
4. Check Vercel deployment logs for specific error

### Issue: Render Deployment Spins Down

**Error**: API Server slow or times out (free tier)

**Solutions**:
1. Render free tier spins down after 15 minutes of inactivity
2. First request after spin-down takes ~30 seconds
3. Consider upgrading to paid tier for always-on
4. Use health check pings to keep alive (UptimeRobot)

## Next Steps

### Phase 2: Implementation Tasks

After verifying the setup works locally, proceed to implementation:

```bash
# Generate detailed task breakdown
/sp.tasks

# Execute tasks with TDD workflow
/sp.implement
```

### Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/profile-management`
2. **Start Both Backends**:
   ```bash
   # Terminal 1: Auth Server
   cd auth-server && npm run dev

   # Terminal 2: API Server
   cd backend && uvicorn src.main:app --reload
   ```
3. **Start Frontend**:
   ```bash
   # Terminal 3: Frontend
   cd book && npm start
   ```
4. **Write Test First**: Create failing test
5. **Implement Feature**: Write minimal code to pass test
6. **Run Tests**:
   ```bash
   # Auth Server
   cd auth-server && npm test

   # API Server
   cd backend && pytest

   # Frontend
   cd book && npm test
   ```
7. **Commit Changes**: `git commit -m "feat(profile): add background form"`
8. **Push and PR**: `git push origin feature/profile-management`

### Useful Commands

```bash
# Auth Server (Node.js)
cd auth-server
npm run dev                    # Dev server with hot reload
npm test                       # Run tests
npm run build                  # Build for production
npx prisma studio              # Database UI

# API Server (FastAPI)
cd backend
uvicorn src.main:app --reload  # Dev server with hot reload
pytest                         # Run all tests
pytest -v -s                   # Verbose with print statements
pytest --cov=src               # Test coverage report
alembic upgrade head           # Apply migrations

# Frontend (Docusaurus)
cd book
npm start                      # Dev server
npm test                       # Run all tests
npm run build                  # Production build
npm run serve                  # Serve production build locally

# Database
psql $DATABASE_URL             # Connect to database
npx prisma studio              # Visual database browser (from auth-server/)

# Both Backends Health Check
curl http://localhost:3000/health && curl http://localhost:8000/health
```

## References

- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/)
- [Research Document](./research.md)
- [better-auth.com Documentation](https://www.better-auth.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Prisma Documentation](https://www.prisma.io/docs/)
- [Docusaurus Documentation](https://docusaurus.io/)
- [Vercel Documentation](https://vercel.com/docs)
- [Render Documentation](https://render.com/docs)
