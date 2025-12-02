# Research: Personalized Authentication and Content

**Feature**: 004-personalized-auth
**Date**: 2025-12-02
**Status**: Phase 0 Complete

## Overview

This document consolidates research findings for implementing personalized authentication with better-auth.com and adaptive content delivery based on user experience levels. All technical decisions documented here resolve the "NEEDS CLARIFICATION" items from the Technical Context section of plan.md.

## 1. better-auth.com Integration with Node.js Auth Server

### Decision
**Create dedicated Node.js/TypeScript authentication server with better-auth.com library**

### Rationale
- better-auth.com is a **JavaScript/TypeScript library**, NOT an external HTTP service
- Requires Node.js runtime (no Python SDK exists or planned)
- Provides type-safe authentication with built-in security patterns
- Handles password hashing, JWT generation, session management automatically
- Supports multiple authentication providers (email/password, OAuth, etc.)

### Microservices Architecture
```
┌─────────────┐
│  Frontend   │
│  (React)    │
└──────┬──────┘
       │
       ├──────────────────┬────────────────────┐
       │                  │                    │
       ▼                  ▼                    ▼
┌──────────────┐   ┌─────────────┐   ┌──────────────┐
│ Auth Server  │   │ API Server  │   │   Content    │
│  (Node.js)   │   │  (FastAPI)  │   │ (Static MDX) │
│              │   │             │   │              │
│ better-auth  │   │ JWT Validate│   │ GitHub Pages │
│ JWT Issue    │   │ Profiles    │   │              │
└──────┬───────┘   │ Personalize │   └──────────────┘
       │           └──────┬──────┘
       │                  │
       └────────┬─────────┘
                ▼
       ┌─────────────────┐
       │   PostgreSQL    │
       │     (Neon)      │
       │ Shared Database │
       └─────────────────┘
```

### Implementation Approach

**Auth Server (Node.js/TypeScript)**:
```typescript
// auth-server/src/auth/auth.config.ts
import { betterAuth } from "better-auth";
import { Pool } from "pg";

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set to true in production
  },
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // Refresh daily
  },
  jwt: {
    secret: process.env.JWT_SECRET,
    expiresIn: "7d",
  },
});

// auth-server/src/index.ts
import express from "express";
import { auth } from "./auth/auth.config";

const app = express();
app.use(express.json());

// Mount better-auth routes (handles /signup, /signin, /signout automatically)
app.use("/auth", auth.handler);

// Custom endpoint to get user info
app.get("/auth/me", async (req, res) => {
  const session = await auth.api.getSession({ headers: req.headers });
  if (!session) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  res.json({ userId: session.user.id, email: session.user.email });
});

app.listen(3000, () => {
  console.log("Auth server running on port 3000");
});
```

**API Server (FastAPI) - JWT Validation Only**:
```python
# backend/src/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Validate JWT token issued by Auth Server"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
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

# Usage in profile endpoints
@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    # Query user_profiles table...
```

### Alternatives Considered
- **Single FastAPI backend with custom auth**: Rejected - violates requirement to use better-auth.com
- **Auth0/Clerk**: Rejected - better-auth.com specified in requirements, cost concerns
- **Firebase Auth**: Rejected - vendor lock-in, not specified in requirements
- **Replace FastAPI with Node.js**: Rejected - breaks existing RAG chatbot backend

### Best Practices
- **Shared JWT secret**: Both Auth Server and API Server use same secret for token signing/validation
- **Shared database**: Both services connect to same PostgreSQL instance (different table ownership)
- **No inter-service HTTP calls**: Auth Server issues JWT, API Server validates JWT locally (no latency)
- **Environment variables**: Store JWT secret, database URL in `.env` (never commit)
- **Type safety**: Use TypeScript in Auth Server for better-auth.com typings
- **Error handling**: Implement consistent error responses across both backends

**References**:
- better-auth.com Documentation: https://www.better-auth.com/docs
- JWT Best Practices: https://datatracker.ietf.org/doc/html/rfc8725
- Express.js Guide: https://expressjs.com/
- python-jose JWT: https://python-jose.readthedocs.io/

---

## 2. better-auth.com JavaScript SDK for React/Docusaurus

### Decision
**Use @better-auth/react package for client-side authentication**

### Rationale
- Official React SDK provides hooks (`useAuth`, `useSession`) for auth state management
- Handles token storage, refresh, and auto-renewal
- Integrates seamlessly with React Context pattern
- Provides TypeScript typings out of the box

### Implementation Approach
```tsx
// Example: Setup better-auth provider
import { BetterAuthProvider } from '@better-auth/react';

function App() {
  return (
    <BetterAuthProvider
      domain="your-app.better-auth.com"
      clientId={process.env.BETTER_AUTH_CLIENT_ID}
    >
      <YourApp />
    </BetterAuthProvider>
  );
}

// Usage in components
import { useAuth } from '@better-auth/react';

function SignupForm() {
  const { signUp, isLoading } = useAuth();

  const handleSubmit = async (data) => {
    await signUp({ email: data.email, password: data.password });
  };
}
```

### Alternatives Considered
- **Manual JWT management**: Rejected due to token refresh complexity
- **Custom React Context**: Rejected due to reinventing well-tested auth flows

### Best Practices
- Store tokens in httpOnly cookies (not localStorage) for XSS protection
- Use better-auth SDK's built-in token refresh mechanism
- Implement auth loading states to prevent flash of unauthenticated content
- Use React Suspense boundaries for async auth checks

**References**:
- @better-auth/react docs
- React Authentication Best Practices: https://react.dev/learn/managing-state#sharing-state-between-components

---

## 3. Session Management Strategy

### Decision
**Hybrid approach: httpOnly cookies for tokens + sessionStorage for UI state**

### Rationale
- **httpOnly cookies**: Secure token storage, protected from XSS attacks
- **sessionStorage**: Store non-sensitive UI state (tab preference, last visited chapter)
- Aligns with 7-day session duration requirement (NFR-007)
- Enables graceful degradation when better-auth is unavailable (NFR-017)

### Implementation Approach
```typescript
// Token storage (handled by better-auth SDK)
// - Access token in httpOnly cookie
// - Refresh token in httpOnly cookie

// UI state storage
const saveTabPreference = (tabName: 'original' | 'personalized') => {
  sessionStorage.setItem('contentTab', tabName);
};

const getTabPreference = () => {
  return sessionStorage.getItem('contentTab') || 'original';
};
```

### Alternatives Considered
- **localStorage only**: Rejected due to XSS vulnerability for tokens
- **sessionStorage only**: Rejected because tokens would be lost on page refresh
- **Server-side sessions**: Rejected due to GitHub Pages static hosting constraint

### Best Practices
- Never store tokens in localStorage or sessionStorage
- Clear sessionStorage on explicit logout (not on tab close)
- Implement session timeout warnings before expiration (at 6.5 days)
- Use secure, SameSite=Strict cookie flags

**References**:
- OWASP Session Management Cheat Sheet
- MDN Web Storage API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API

---

## 4. Docusaurus Content Variant Rendering with MDX

### Decision
**Dynamic MDX imports with React Context for variant selection**

### Rationale
- Docusaurus supports MDX (Markdown + JSX) for rich content
- React Context provides global state for experience level
- Dynamic imports enable loading correct variant without page reload
- Aligns with <500ms tab switching requirement (NFR-005)

### Implementation Approach
```tsx
// ContentTabs component
import { lazy, Suspense } from 'react';
import { usePersonalization } from '@site/src/hooks/usePersonalization';

function ContentTabs({ chapterPath }) {
  const { experienceLevel } = usePersonalization();
  const [activeTab, setActiveTab] = useState('original');

  const OriginalContent = lazy(() => import(`@site/docs/${chapterPath}/index.md`));
  const PersonalizedContent = lazy(() =>
    import(`@site/docs/${chapterPath}/${experienceLevel}.md`)
  );

  return (
    <div>
      <Tabs>
        <Tab active={activeTab === 'original'} onClick={() => setActiveTab('original')}>
          Original Content
        </Tab>
        <Tab active={activeTab === 'personalized'} onClick={() => setActiveTab('personalized')}>
          Personalized for You
        </Tab>
      </Tabs>

      <Suspense fallback={<LoadingSpinner />}>
        {activeTab === 'original' ? <OriginalContent /> : <PersonalizedContent />}
      </Suspense>
    </div>
  );
}
```

### Alternatives Considered
- **Server-side rendering**: Rejected due to GitHub Pages static hosting
- **Compile-time variant selection**: Rejected because can't adapt to user login state
- **Separate pages per variant**: Rejected due to poor UX (page reload required)

### Best Practices
- Preload personalized content on page load to avoid delay on tab switch
- Use Suspense boundaries with meaningful loading indicators
- Implement error boundaries for missing variant files
- Cache imported MDX modules in React state

**References**:
- Docusaurus MDX Guide: https://docusaurus.io/docs/markdown-features
- React lazy & Suspense: https://react.dev/reference/react/lazy

---

## 5. PostgreSQL Schema for User Profiles with Multi-valued Fields

### Decision
**Use JSONB columns for array fields (languages, frameworks, platforms, sensors)**

### Rationale
- PostgreSQL JSONB provides flexible storage for variable-length arrays
- Supports indexing with GIN indexes for fast lookups
- Allows querying array contents without complex JOINs
- Simplifies schema evolution (adding new tech options)
- Neon Postgres (existing) fully supports JSONB

### Implementation Approach
```sql
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id),

    -- Software background
    programming_languages JSONB DEFAULT '[]'::jsonb,  -- ["Python", "C++", "Java"]
    frameworks JSONB DEFAULT '[]'::jsonb,             -- ["ROS 2", "TensorFlow"]
    software_experience_years INTEGER NOT NULL,

    -- Hardware background
    robotics_platforms JSONB DEFAULT '[]'::jsonb,     -- ["Arduino", "Raspberry Pi"]
    sensors_actuators JSONB DEFAULT '[]'::jsonb,      -- ["LiDAR", "IMU"]
    hardware_experience_years INTEGER NOT NULL,

    -- Derived fields (cached)
    derived_experience_level VARCHAR(20) NOT NULL,    -- 'Beginner', 'Intermediate', 'Advanced'

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    CONSTRAINT check_experience_level CHECK (
        derived_experience_level IN ('Beginner', 'Intermediate', 'Advanced')
    )
);

-- GIN index for fast JSONB queries
CREATE INDEX idx_programming_languages ON user_profiles USING GIN (programming_languages);
CREATE INDEX idx_derived_experience ON user_profiles (derived_experience_level);
```

### Alternatives Considered
- **Separate junction tables**: Rejected due to query complexity (many JOINs)
- **PostgreSQL arrays**: Rejected because JSONB offers better querying and indexing
- **Comma-separated strings**: Rejected due to poor query performance and data integrity

### Best Practices
- Use GIN indexes on JSONB columns for `?` (contains) and `@>` (contains array) queries
- Validate JSONB structure at application layer (Pydantic models)
- Store lowercase values for case-insensitive matching
- Use database triggers to auto-update `updated_at` timestamp

**References**:
- PostgreSQL JSONB Guide: https://www.postgresql.org/docs/current/datatype-json.html
- Neon Postgres JSONB support: https://neon.tech/docs/postgres/jsonb

---

## 6. Experience Level Calculation Algorithm (Conservative Matching)

### Decision
**Pure function with software/hardware level comparison, return minimum**

### Rationale
- Simple, deterministic algorithm easy to test
- Idempotent - same inputs always produce same output
- Conservative approach prevents overwhelming users with knowledge gaps
- Aligns with educational best practices (ZPD - Zone of Proximal Development)

### Implementation Approach
```python
from enum import Enum

class ExperienceLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

def calculate_experience_level(
    software_years: int,
    hardware_years: int
) -> ExperienceLevel:
    """
    Calculate derived experience level using conservative matching.

    Returns the lower of software and hardware experience levels
    to ensure content remains accessible.
    """
    def years_to_level(years: int) -> ExperienceLevel:
        if years >= 5:
            return ExperienceLevel.ADVANCED
        elif years >= 2:
            return ExperienceLevel.INTERMEDIATE
        else:
            return ExperienceLevel.BEGINNER

    software_level = years_to_level(software_years)
    hardware_level = years_to_level(hardware_years)

    # Return minimum level (most conservative)
    level_order = [
        ExperienceLevel.BEGINNER,
        ExperienceLevel.INTERMEDIATE,
        ExperienceLevel.ADVANCED
    ]

    software_idx = level_order.index(software_level)
    hardware_idx = level_order.index(hardware_level)

    return level_order[min(software_idx, hardware_idx)]

# Test cases
assert calculate_experience_level(6, 1) == ExperienceLevel.BEGINNER  # Advanced + Beginner = Beginner
assert calculate_experience_level(3, 4) == ExperienceLevel.INTERMEDIATE  # Intermediate + Intermediate
assert calculate_experience_level(7, 8) == ExperienceLevel.ADVANCED  # Advanced + Advanced
```

### Alternatives Considered
- **Use higher level**: Rejected because overwhelming users with content above their capability
- **Average the levels**: Rejected because "Intermediate" average doesn't help Beginner in one domain
- **Weighted average by domain**: Rejected due to complexity and unclear benefits

### Best Practices
- Store calculation in database (cached) to avoid recalculating on every request
- Recalculate only on profile update (FR-009)
- Log level changes for analytics
- Provide UI feedback showing how experience levels map to content

**References**:
- Zone of Proximal Development (Vygotsky): https://en.wikipedia.org/wiki/Zone_of_proximal_development
- Adaptive Learning Best Practices

---

## 7. Tab-Based Content UI Patterns in React

### Decision
**Controlled tabs component with keyboard navigation and accessibility**

### Rationale
- Accessible to keyboard users and screen readers (WCAG 2.1 Level AA, NFR-011)
- Smooth transitions without page reload (<500ms, NFR-005)
- Preserves tab selection across navigation (sessionStorage)
- Standard React pattern, easy to maintain

### Implementation Approach
```tsx
// Accessible tabs component
import { useState, useRef } from 'react';

interface TabsProps {
  defaultTab?: 'original' | 'personalized';
  onTabChange?: (tab: string) => void;
  children: React.ReactNode;
}

function ContentTabs({ defaultTab = 'original', onTabChange, children }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  const tabListRef = useRef<HTMLDivElement>(null);

  const handleTabClick = (tabName: string) => {
    setActiveTab(tabName);
    onTabChange?.(tabName);
    sessionStorage.setItem('activeContentTab', tabName);
  };

  const handleKeyDown = (event: React.KeyboardEvent, tabName: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleTabClick(tabName);
    }
    // Arrow key navigation
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      // Navigate to prev/next tab
    }
  };

  return (
    <div className="content-tabs">
      <div
        role="tablist"
        aria-label="Content view options"
        ref={tabListRef}
      >
        <button
          role="tab"
          aria-selected={activeTab === 'original'}
          aria-controls="original-panel"
          tabIndex={activeTab === 'original' ? 0 : -1}
          onClick={() => handleTabClick('original')}
          onKeyDown={(e) => handleKeyDown(e, 'original')}
        >
          Original Content
        </button>
        <button
          role="tab"
          aria-selected={activeTab === 'personalized'}
          aria-controls="personalized-panel"
          tabIndex={activeTab === 'personalized' ? 0 : -1}
          onClick={() => handleTabClick('personalized')}
          onKeyDown={(e) => handleKeyDown(e, 'personalized')}
        >
          Personalized for You
        </button>
      </div>

      <div role="tabpanel" id="original-panel" hidden={activeTab !== 'original'}>
        {/* Original content */}
      </div>
      <div role="tabpanel" id="personalized-panel" hidden={activeTab !== 'personalized'}>
        {/* Personalized content */}
      </div>
    </div>
  );
}
```

### Alternatives Considered
- **Separate pages**: Rejected due to page reload overhead and poor UX
- **Toggle switch**: Rejected because doesn't clearly show two distinct options
- **Dropdown menu**: Rejected due to extra click and hidden options

### Best Practices
- Use proper ARIA roles (`tablist`, `tab`, `tabpanel`)
- Implement keyboard navigation (Arrow keys, Home, End)
- Ensure focus management when switching tabs
- Use CSS transitions for smooth visual feedback
- Preload inactive tab content to avoid loading delay

**References**:
- W3C ARIA Tabs Pattern: https://www.w3.org/WAI/ARIA/apg/patterns/tabs/
- React Accessibility: https://react.dev/learn/accessibility

---

## 8. Graceful Degradation for External Service Failures

### Decision
**Circuit breaker pattern + local session validation + fallback UI**

### Rationale
- Maintains existing user sessions when better-auth is down (NFR-017)
- New signups/logins fail gracefully with clear messaging
- Unauthenticated users can still access original content
- Detects failures within 5 seconds and displays appropriate errors

### Implementation Approach
```python
# Circuit breaker for better-auth API calls
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, stop calling
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise ServiceUnavailableError("better-auth service is unavailable")

        try:
            result = await func(*args, **kwargs)
            # Success - reset circuit
            self.failure_count = 0
            self.state = CircuitState.CLOSED
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise e

# Usage in FastAPI
better_auth_circuit = CircuitBreaker()

@router.post("/signup")
async def signup(user_data: UserCreate):
    try:
        result = await better_auth_circuit.call(
            register_with_better_auth,
            user_data.email,
            user_data.password
        )
        return result
    except ServiceUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="Authentication service temporarily unavailable. Please try again later."
        )
```

Frontend handling:
```typescript
// Frontend error boundary for auth failures
function AuthErrorBoundary({ children }) {
  const [hasError, setHasError] = useState(false);

  if (hasError) {
    return (
      <div role="alert">
        <h2>Authentication Temporarily Unavailable</h2>
        <p>
          We're experiencing technical difficulties with our authentication service.
          You can still read the original content without signing in.
        </p>
        <button onClick={() => navigate('/docs')}>
          Browse Content as Guest
        </button>
      </div>
    );
  }

  return children;
}
```

### Alternatives Considered
- **No fallback**: Rejected because breaks user experience entirely
- **Local-only auth backup**: Rejected due to security complexity
- **Queue requests**: Rejected because auth must be real-time

### Best Practices
- Set circuit breaker thresholds based on expected service SLA
- Log all circuit state changes for monitoring
- Provide clear user messaging with alternative actions
- Test degraded mode scenarios in staging

**References**:
- Circuit Breaker Pattern: https://martinfowler.com/bliki/CircuitBreaker.html
- FastAPI Error Handling: https://fastapi.tiangolo.com/tutorial/handling-errors/

---

## 9. Password Strength Validation (Client + Server)

### Decision
**Implement validation on both client (immediate feedback) and server (security)****

### Rationale
- Client-side: Instant feedback, better UX
- Server-side: Security enforcement, can't be bypassed
- Double validation prevents weak passwords (NFR-001)
- Meets requirements: 8+ chars, uppercase, lowercase, number

### Implementation Approach
```typescript
// Client-side (Zod schema)
import { z } from 'zod';

const passwordSchema = z.string()
  .min(8, "Password must be at least 8 characters")
  .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
  .regex(/[a-z]/, "Password must contain at least one lowercase letter")
  .regex(/[0-9]/, "Password must contain at least one number");

const signupSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: passwordSchema,
  confirmPassword: z.string()
}).refine(data => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"]
});
```

```python
# Server-side (Pydantic)
from pydantic import BaseModel, field_validator
import re

class UserCreate(BaseModel):
    email: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain number')
        return v
```

### Alternatives Considered
- **Client-only validation**: Rejected due to security bypass risk
- **Server-only validation**: Rejected due to poor UX (delayed feedback)
- **More complex requirements**: Rejected to balance security with usability

### Best Practices
- Show password strength meter as user types
- Provide specific error messages for each requirement
- Never log or store passwords in plaintext
- Use bcrypt with appropriate cost factor (12-14 rounds)

**References**:
- OWASP Password Guidelines: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- Zod validation: https://zod.dev/

---

## 10. Profile Form UX for Multi-select Lists

### Decision
**Checkbox group with search/filter + "Other" text input**

### Rationale
- Easy to scan predefined options quickly
- Search/filter helps with long lists (20+ options)
- "Other" field provides flexibility for uncommon selections
- Accessible with keyboard and screen readers
- Mobile-friendly (larger touch targets than dropdowns)

### Implementation Approach
```tsx
// Multi-select with search
import { useState } from 'react';

interface MultiSelectProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  label: string;
  placeholder?: string;
}

function MultiSelect({ options, selected, onChange, label, placeholder }: MultiSelectProps) {
  const [search, setSearch] = useState('');
  const [otherValue, setOtherValue] = useState('');

  const filteredOptions = options.filter(opt =>
    opt.toLowerCase().includes(search.toLowerCase())
  );

  const handleToggle = (option: string) => {
    if (selected.includes(option)) {
      onChange(selected.filter(s => s !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  const handleAddOther = () => {
    if (otherValue && !selected.includes(otherValue)) {
      onChange([...selected, otherValue]);
      setOtherValue('');
    }
  };

  return (
    <div className="multi-select">
      <label>{label}</label>

      <input
        type="search"
        placeholder={placeholder || "Search options..."}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        aria-label={`Search ${label}`}
      />

      <div role="group" aria-labelledby={`${label}-group`}>
        {filteredOptions.map(option => (
          <label key={option} className="checkbox-label">
            <input
              type="checkbox"
              checked={selected.includes(option)}
              onChange={() => handleToggle(option)}
              aria-label={option}
            />
            {option}
          </label>
        ))}
      </div>

      <div className="other-input">
        <input
          type="text"
          placeholder="Other (specify)"
          value={otherValue}
          onChange={(e) => setOtherValue(e.target.value)}
          aria-label={`Other ${label}`}
        />
        <button onClick={handleAddOther} aria-label="Add custom option">
          Add
        </button>
      </div>

      {selected.length > 0 && (
        <div className="selected-tags">
          {selected.map(item => (
            <span key={item} className="tag">
              {item}
              <button
                onClick={() => handleToggle(item)}
                aria-label={`Remove ${item}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Alternatives Considered
- **Dropdown multi-select**: Rejected due to poor mobile UX and limited visibility
- **Tags input only**: Rejected because users might not know all options
- **Autocomplete**: Rejected due to implementation complexity and accessibility challenges

### Best Practices
- Limit visible options to 8-10, require search for more
- Show selected items as removable tags
- Provide clear "Select all" / "Clear all" options for long lists
- Use debouncing for search input (300ms delay)
- Make checkboxes large enough for mobile (44×44px minimum)

**References**:
- React Hook Form: https://react-hook-form.com/
- Accessible Forms: https://www.w3.org/WAI/tutorials/forms/

---

## Technology Summary

| Category | Technology | Status | Rationale |
|----------|-----------|--------|-----------|
| Backend Auth | better-auth.com via HTTP API | ✅ Selected | Industry-standard, reduces security burden |
| Frontend Auth | @better-auth/react | ✅ Selected | Official SDK, TypeScript support |
| Session Storage | httpOnly cookies + sessionStorage | ✅ Selected | Balance security and UX |
| Content Rendering | MDX dynamic imports | ✅ Selected | Fast, no page reload, Docusaurus native |
| Database Schema | PostgreSQL JSONB for arrays | ✅ Selected | Flexible, queryable, Neon supported |
| Experience Calc | Pure function, conservative min | ✅ Selected | Simple, testable, educational best practice |
| UI Pattern | Accessible tab component | ✅ Selected | WCAG 2.1 AA compliant, keyboard nav |
| Degradation | Circuit breaker + fallback UI | ✅ Selected | Graceful, user-friendly, measurable |
| Password Validation | Client (Zod) + Server (Pydantic) | ✅ Selected | Immediate feedback + security |
| Form UX | Checkbox groups + search + Other | ✅ Selected | Accessible, mobile-friendly, flexible |

---

## 11. Cross-Platform Deployment Strategy

### Decision
**Deploy Auth Server (Node.js) on Vercel, API Server (Python) on Render**

### Rationale
- **Auth Server on Vercel**: Optimized for Node.js/TypeScript serverless functions, excellent free tier, instant cold starts
- **API Server on Render**: Already deployed (existing RAG chatbot), Python runtime support
- **Separate platforms**: Maximizes free tier limits, isolated failure domains, independent scaling
- **Shared resources**: Both connect to same Neon PostgreSQL, share JWT secret

### Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│               Frontend (GitHub Pages)                        │
│           https://username.github.io/book                    │
└────────────────┬────────────────────┬──────────────────────┘
                 │                    │
      ┌──────────▼────────┐    ┌─────▼──────────────────┐
      │  Auth Server      │    │  API Server            │
      │  (Node.js)        │    │  (FastAPI)             │
      │                   │    │                        │
      │  Platform: Vercel │    │  Platform: Render      │
      │  Port: 3000       │    │  Port: 8000            │
      │  URL: auth-*.     │    │  URL: api-*.           │
      │       vercel.app  │    │       onrender.com     │
      └──────────┬────────┘    └─────┬──────────────────┘
                 │                   │
                 └─────────┬─────────┘
                           ▼
                ┌─────────────────────┐
                │  Neon PostgreSQL    │
                │  (Shared Database)  │
                │  Serverless Postgres│
                └─────────────────────┘
```

### Platform Comparison

| Feature | Vercel (Auth Server) | Render (API Server) |
|---------|---------------------|---------------------|
| **Free Tier** | 100GB bandwidth/month | 750 hours/month |
| **Cold Start** | ~0ms (serverless) | ~30s (spins down after 15min) |
| **Best For** | Node.js/TypeScript | Python/FastAPI |
| **Build Time** | Fast (1-2 min) | Medium (3-5 min) |
| **Custom Domain** | Yes (free HTTPS) | Yes (free HTTPS) |
| **Environment Vars** | Yes | Yes |
| **Database Support** | Via connection string | Via connection string |

### Deployment Configuration

#### Auth Server (Vercel)

**vercel.json**:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "src/index.ts",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/auth/(.*)",
      "dest": "src/index.ts"
    }
  ],
  "env": {
    "NODE_ENV": "production"
  }
}
```

**Environment Variables (Vercel Dashboard)**:
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db?sslmode=require
JWT_SECRET=your-super-secret-key-min-32-chars-SAME-AS-API-SERVER
CORS_ORIGINS=https://username.github.io,http://localhost:3000
```

**Deployment Command**:
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from auth-server directory
cd auth-server
vercel --prod
```

#### API Server (Render)

**render.yaml** (if using Infrastructure as Code):
```yaml
services:
  - type: web
    name: api-server
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: JWT_SECRET
        sync: false
      - key: CORS_ORIGINS
        value: https://username.github.io,http://localhost:3000
```

**Environment Variables (Render Dashboard)**:
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db?sslmode=require
JWT_SECRET=your-super-secret-key-min-32-chars-SAME-AS-AUTH-SERVER
CORS_ORIGINS=https://username.github.io,http://localhost:3000
```

#### Frontend (GitHub Pages)

**Environment Variables** (GitHub Secrets → Actions):
```bash
REACT_APP_AUTH_SERVER_URL=https://auth-yourbook.vercel.app
REACT_APP_API_SERVER_URL=https://api-yourbook.onrender.com
```

**Build Configuration** (`.github/workflows/deploy.yml`):
```yaml
- name: Build
  env:
    REACT_APP_AUTH_SERVER_URL: ${{ secrets.AUTH_SERVER_URL }}
    REACT_APP_API_SERVER_URL: ${{ secrets.API_SERVER_URL }}
  run: npm run build
```

### Critical Requirements

#### 1. Shared JWT Secret (CRITICAL)
Both backends MUST use **identical** JWT secret:
```bash
# Generate strong secret (32+ characters)
openssl rand -base64 32

# Set in BOTH Vercel and Render
JWT_SECRET=<same-value-on-both-platforms>
```

#### 2. CORS Configuration

**Auth Server (Vercel)**:
```typescript
// auth-server/src/index.ts
import cors from 'cors';

app.use(cors({
  origin: process.env.CORS_ORIGINS?.split(',') || [
    'https://username.github.io',
    'http://localhost:3000'
  ],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));
```

**API Server (Render - already configured)**:
```python
# backend/src/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 3. Database Connection

Both backends connect to **same Neon PostgreSQL**:
```bash
# Same DATABASE_URL in both Vercel and Render
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/db?sslmode=require
```

### Deployment Workflow

```mermaid
graph TD
    A[Code Push to GitHub] --> B{Which Backend?}
    B -->|auth-server/| C[Vercel Auto-Deploy]
    B -->|backend/| D[Render Auto-Deploy]
    B -->|book/| E[GitHub Actions]
    C --> F[Auth Server Live]
    D --> G[API Server Live]
    E --> H[Frontend Live]
    F --> I[Test Auth Endpoints]
    G --> J[Test API Endpoints]
    H --> K[Test E2E Flows]
```

### Monitoring and Health Checks

**Auth Server (Vercel)**:
```typescript
// auth-server/src/index.ts
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'auth-server',
    timestamp: new Date().toISOString()
  });
});
```

**API Server (Render - existing)**:
```python
# backend/src/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "api-server",
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Health Check URLs**:
- Auth Server: `https://auth-yourbook.vercel.app/health`
- API Server: `https://api-yourbook.onrender.com/health`

### Cost Analysis (Free Tier)

| Platform | Free Tier Limit | Estimated Usage | Headroom |
|----------|----------------|-----------------|----------|
| **Vercel** | 100GB bandwidth/month | ~5GB (auth only) | ✅ 95GB available |
| **Render** | 750 hours/month | ~720 hours (always-on) | ⚠️ 30 hours buffer |
| **Neon** | 3GB storage, 100 hours compute | ~500MB, 50 hours | ✅ Plenty of headroom |
| **GitHub Pages** | 100GB bandwidth/month | ~10GB (static) | ✅ 90GB available |

**Total Cost**: $0/month (within free tiers)

### Alternatives Considered
- **Both on Render**: Rejected - would exceed 750 hour free tier limit faster
- **Both on Vercel**: Rejected - Vercel not optimized for Python/FastAPI
- **Railway**: Rejected - $5 credit expires after first month
- **Fly.io**: Rejected - more complex setup than Vercel

### Best Practices
- **Environment parity**: Use same DATABASE_URL and JWT_SECRET across all environments
- **Health checks**: Monitor both /health endpoints with UptimeRobot or similar
- **Logging**: Enable structured logging in both backends for debugging
- **Deployment order**: Deploy Auth Server first, then API Server, then Frontend
- **Rollback strategy**: Keep previous Vercel deployments available for instant rollback

**References**:
- Vercel Documentation: https://vercel.com/docs
- Render Documentation: https://render.com/docs
- Neon Postgres: https://neon.tech/docs

## Risk Mitigation

| Risk | Mitigation Strategy | Acceptance Criteria |
|------|---------------------|---------------------|
| better-auth.com downtime | Circuit breaker, existing sessions continue | <5s failure detection, clear error messaging |
| Slow tab switching | Preload variants, React.lazy with Suspense | <500ms switch time measured |
| Complex profile forms | Search/filter, progressive disclosure, clear labels | 90% signup completion rate (SC-008) |
| Poor content matching | Conservative algorithm, user can always see original | 70% use personalized tab (SC-005) |
| Security vulnerabilities | Dual validation, httpOnly cookies, external auth service | Zero unauthorized access (SC-007) |

## Next Steps

1. ✅ Research complete - all NEEDS CLARIFICATION resolved
2. ⏭️ Proceed to Phase 1: Design & Contracts (data-model.md, contracts/, quickstart.md)
3. ⏭️ Create Alembic migration for database schema
4. ⏭️ Implement backend auth module following researched patterns
5. ⏭️ Implement frontend auth components with accessibility features

## References

All inline references included in respective sections above. Key documentation:
- better-auth.com: https://better-auth.com/docs
- FastAPI: https://fastapi.tiangolo.com/
- Docusaurus: https://docusaurus.io/docs
- React: https://react.dev/
- PostgreSQL JSONB: https://www.postgresql.org/docs/current/datatype-json.html
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- OWASP: https://owasp.org/www-project-cheat-sheets/
