# Data Model: Personalized Authentication and Content

**Feature**: 004-personalized-auth
**Date**: 2025-12-02
**Status**: Phase 1 Design

## Overview

This document defines the database schema, entities, relationships, and validation rules for the personalized authentication feature. The schema extends the existing Neon Postgres database used by the RAG chatbot.

## Architecture: Shared Database, Distributed Ownership

The feature uses a **microservices architecture** with two backends sharing a single PostgreSQL database:

```
┌────────────────────────────────────────────────────────────────┐
│                   Neon PostgreSQL (Shared)                      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Auth Server Tables (Node.js manages)                   │  │
│  │  - users (authentication credentials)                    │  │
│  │  - user_sessions (JWT tokens, expiry)                    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  API Server Tables (FastAPI manages)                     │  │
│  │  - user_profiles (background info, derived level)        │  │
│  │  - tab_preferences (content tab selection)               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Existing Tables (unchanged)                             │  │
│  │  - chatbot-related tables                                │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
         ▲                                    ▲
         │                                    │
         │                                    │
┌────────┴────────┐                ┌─────────┴──────────┐
│  Auth Server    │                │   API Server       │
│  (Node.js)      │                │   (FastAPI)        │
│                 │                │                    │
│  Platform:      │                │   Platform:        │
│  Vercel         │                │   Render           │
└─────────────────┘                └────────────────────┘
```

### Table Ownership Model

| Table | Owner | Managed By | Accessed By | Operations |
|-------|-------|------------|-------------|------------|
| **users** | Auth Server | better-auth.com (Node.js) | Auth Server (RW), API Server (R) | Signup, Signin, Password changes |
| **user_sessions** | Auth Server | better-auth.com (Node.js) | Auth Server (RW) | Session creation, validation, cleanup |
| **user_profiles** | API Server | FastAPI | API Server (RW) | Profile CRUD, experience calculation |
| **tab_preferences** | API Server | FastAPI | API Server (RW) | Tab selection persistence |

### Key Design Principles

1. **Single Source of Truth**: Each table has ONE owner responsible for writes
2. **Read-Only Cross-Access**: API Server can read `users` table (via user_id from JWT), but never writes to it
3. **No Circular Dependencies**: Auth Server never accesses API Server tables
4. **JWT as Bridge**: Auth Server issues JWT with `user_id`, API Server uses it to query its own tables
5. **Shared Connection**: Both backends connect to same DATABASE_URL (Neon Postgres)

### Communication Pattern

**Signup Flow**:
```
1. Frontend → Auth Server: POST /auth/signup {email, password}
2. Auth Server: Insert into `users` table via better-auth.com
3. Auth Server: Insert into `user_sessions` table
4. Auth Server → Frontend: JWT token with user_id
5. Frontend → API Server: POST /api/profile {background} + JWT
6. API Server: Decode JWT → get user_id
7. API Server: Insert into `user_profiles` table
8. API Server → Frontend: Profile data
```

**Profile Update Flow**:
```
1. Frontend → API Server: PUT /api/profile {updates} + JWT
2. API Server: Decode JWT → get user_id (NO call to Auth Server)
3. API Server: Update `user_profiles` table
4. API Server → Frontend: Updated profile
```

**Key Point**: API Server validates JWT **locally** (shared secret) - no network call to Auth Server needed.

## Entity Relationship Diagram

```
┌─────────────┐          ┌──────────────────┐
│    users    │ 1      1 │  user_profiles   │
│             │◄─────────┤                  │
│ - id (PK)   │          │ - user_id (FK)   │
│ - email     │          │ - prog_langs     │
│ - password  │          │ - frameworks     │
│ - status    │          │ - sw_exp_years   │
│ - created   │          │ - platforms      │
└─────────────┘          │ - sensors        │
      │                  │ - hw_exp_years   │
      │                  │ - derived_level  │
      │ 1                └──────────────────┘
      │
      │
      │ N
      ▼
┌─────────────────┐
│  user_sessions  │
│                 │
│ - id (PK)       │
│ - user_id (FK)  │
│ - token         │
│ - expires_at    │
│ - created_at    │
└─────────────────┘
      │
      │ 1
      │
      │ 1
      ▼
┌─────────────────┐
│ tab_preferences │
│                 │
│ - user_id (FK)  │
│ - active_tab    │
│ - updated_at    │
└─────────────────┘
```

## Database Tables

### 1. users

**Owner**: 🟦 **Auth Server** (Node.js/Vercel) - Managed by better-auth.com
**Access**: Auth Server (RW), API Server (Read-only for user_id lookups)

**Purpose**: Store authentication credentials and account status.

**Schema**:
```sql
CREATE TABLE users (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Authentication
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hashed

    -- Account Status
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,

    -- Constraints
    CONSTRAINT check_status CHECK (status IN ('active', 'suspended', 'deleted')),
    CONSTRAINT check_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Indexes
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status) WHERE status = 'active';
CREATE INDEX idx_users_created_at ON users(created_at DESC);
```

**Fields**:
- `id`: UUID primary key, auto-generated
- `email`: User email address, unique, used for login
- `password_hash`: bcrypt hashed password (not plaintext)
- `status`: Account status (active, suspended, deleted)
- `email_verified`: Whether email has been verified (future enhancement)
- `created_at`: Account creation timestamp
- `updated_at`: Last account modification timestamp
- `last_login_at`: Last successful login timestamp

**Validation Rules**:
- Email must be unique and valid format (regex check)
- Password must meet strength requirements before hashing (8+ chars, uppercase, lowercase, number)
- Status must be one of allowed values
- Timestamps auto-managed by database

**Relationships**:
- One-to-one with `user_profiles`
- One-to-many with `user_sessions`
- One-to-one with `tab_preferences`

---

### 2. user_profiles

**Owner**: 🟩 **API Server** (FastAPI/Render)
**Access**: API Server (RW)

**Purpose**: Store user background information for content personalization.

**Schema**:
```sql
CREATE TABLE user_profiles (
    -- Foreign Key (also Primary Key)
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,

    -- Software Background
    programming_languages JSONB DEFAULT '[]'::jsonb NOT NULL,
    frameworks JSONB DEFAULT '[]'::jsonb NOT NULL,
    software_experience_years INTEGER NOT NULL DEFAULT 0,

    -- Hardware Background
    robotics_platforms JSONB DEFAULT '[]'::jsonb NOT NULL,
    sensors_actuators JSONB DEFAULT '[]'::jsonb NOT NULL,
    hardware_experience_years INTEGER NOT NULL DEFAULT 0,

    -- Derived/Cached Fields
    derived_experience_level VARCHAR(20) NOT NULL DEFAULT 'Beginner',

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT check_experience_level CHECK (
        derived_experience_level IN ('Beginner', 'Intermediate', 'Advanced')
    ),
    CONSTRAINT check_software_years CHECK (software_experience_years >= 0 AND software_experience_years <= 50),
    CONSTRAINT check_hardware_years CHECK (hardware_experience_years >= 0 AND hardware_experience_years <= 50)
);

-- Indexes for performance
CREATE INDEX idx_derived_experience_level ON user_profiles(derived_experience_level);
CREATE INDEX idx_software_experience ON user_profiles(software_experience_years);
CREATE INDEX idx_hardware_experience ON user_profiles(hardware_experience_years);

-- GIN indexes for JSONB array queries
CREATE INDEX idx_programming_languages ON user_profiles USING GIN (programming_languages);
CREATE INDEX idx_frameworks ON user_profiles USING GIN (frameworks);
CREATE INDEX idx_robotics_platforms ON user_profiles USING GIN (robotics_platforms);
CREATE INDEX idx_sensors_actuators ON user_profiles USING GIN (sensors_actuators);
```

**Fields**:
- `user_id`: Foreign key to users table (also primary key)
- `programming_languages`: JSONB array of language names (e.g., ["Python", "C++", "Java"])
- `frameworks`: JSONB array of framework names (e.g., ["ROS 2", "TensorFlow"])
- `software_experience_years`: Integer years of development experience (0-50)
- `robotics_platforms`: JSONB array of platform names (e.g., ["Arduino", "Raspberry Pi"])
- `sensors_actuators`: JSONB array of sensor/actuator names (e.g., ["LiDAR", "IMU"])
- `hardware_experience_years`: Integer years of hardware experience (0-50)
- `derived_experience_level`: Cached result of experience calculation (Beginner/Intermediate/Advanced)
- `created_at`: Profile creation timestamp
- `updated_at`: Last profile modification timestamp

**Validation Rules**:
- All JSONB arrays must be valid JSON arrays (enforced by PostgreSQL)
- Experience years must be non-negative and reasonable (<= 50)
- Derived experience level must be one of three valid values
- Programming languages should be stored in lowercase for consistent matching
- Custom entries from "Other" fields included in JSONB arrays

**Relationships**:
- One-to-one with `users` (mandatory - profile created on signup)

**JSONB Structure Examples**:
```json
{
  "programming_languages": ["python", "c++", "javascript"],
  "frameworks": ["ros 2", "pytorch", "react"],
  "robotics_platforms": ["arduino", "raspberry pi", "nvidia jetson"],
  "sensors_actuators": ["lidar", "depth camera", "imu", "servo motor"]
}
```

---

### 3. user_sessions

**Owner**: 🟦 **Auth Server** (Node.js/Vercel) - Managed by better-auth.com
**Access**: Auth Server (RW)

**Purpose**: Track active user sessions for authentication and session management.

**Schema**:
```sql
CREATE TABLE user_sessions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign Key
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session Data
    token_hash VARCHAR(255) NOT NULL UNIQUE,  -- SHA-256 hash of JWT token
    refresh_token_hash VARCHAR(255),           -- For token refresh
    ip_address INET,
    user_agent TEXT,

    -- Session Lifecycle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    last_activity_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,

    -- Constraints
    CONSTRAINT check_expires_after_created CHECK (expires_at > created_at)
);

-- Indexes
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE UNIQUE INDEX idx_user_sessions_token ON user_sessions(token_hash) WHERE NOT revoked;
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at) WHERE NOT revoked;
CREATE INDEX idx_user_sessions_activity ON user_sessions(last_activity_at DESC);
```

**Fields**:
- `id`: UUID primary key for session
- `user_id`: Foreign key to users table
- `token_hash`: SHA-256 hash of JWT access token (not the token itself for security)
- `refresh_token_hash`: Hash of refresh token for token renewal
- `ip_address`: Client IP address for security audit
- `user_agent`: Client user agent string
- `created_at`: Session creation timestamp
- `expires_at`: Session expiration timestamp (7 days from creation per spec)
- `last_activity_at`: Last request timestamp for activity tracking
- `revoked`: Whether session has been manually revoked (logout)

**Validation Rules**:
- Token hashes must be unique among non-revoked sessions
- Expiration must be after creation
- Sessions expire after 7 days of inactivity (can be renewed)

**Relationships**:
- Many-to-one with `users` (one user can have multiple active sessions)

**Session Lifecycle**:
1. Created on successful login
2. `last_activity_at` updated on each authenticated request
3. Expires after 7 days or manual logout (revoked = true)
4. Cleanup job periodically deletes expired sessions

---

### 4. tab_preferences

**Owner**: 🟩 **API Server** (FastAPI/Render)
**Access**: API Server (RW)

**Purpose**: Store user's last selected content tab (Original/Personalized) for persistence across sessions.

**Schema**:
```sql
CREATE TABLE tab_preferences (
    -- Foreign Key (also Primary Key)
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,

    -- Preference Data
    active_tab VARCHAR(20) NOT NULL DEFAULT 'original',

    -- Timestamps
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT check_active_tab CHECK (active_tab IN ('original', 'personalized'))
);

-- Indexes
CREATE INDEX idx_tab_preferences_updated ON tab_preferences(updated_at DESC);
```

**Fields**:
- `user_id`: Foreign key to users table (also primary key)
- `active_tab`: Last selected tab ('original' or 'personalized')
- `updated_at`: Last tab selection timestamp

**Validation Rules**:
- Active tab must be either 'original' or 'personalized'
- One row per user (enforced by primary key)

**Relationships**:
- One-to-one with `users`

---

## Database Migrations

**Migration Strategy**: Use Alembic for version-controlled schema migrations.

**Initial Migration** (`001_create_auth_tables.py`):
```python
"""Create authentication and profile tables

Revision ID: 001
Create Date: 2025-12-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('email_verified', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('last_login_at', sa.TIMESTAMP, nullable=True),
        sa.CheckConstraint("status IN ('active', 'suspended', 'deleted')", name='check_status'),
        sa.CheckConstraint(
            "email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name='check_email_format'
        )
    )

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('programming_languages', JSONB, nullable=False, server_default="'[]'::jsonb"),
        sa.Column('frameworks', JSONB, nullable=False, server_default="'[]'::jsonb"),
        sa.Column('software_experience_years', sa.Integer, nullable=False, server_default='0'),
        sa.Column('robotics_platforms', JSONB, nullable=False, server_default="'[]'::jsonb"),
        sa.Column('sensors_actuators', JSONB, nullable=False, server_default="'[]'::jsonb"),
        sa.Column('hardware_experience_years', sa.Integer, nullable=False, server_default='0'),
        sa.Column('derived_experience_level', sa.String(20), nullable=False, server_default="'Beginner'"),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint(
            "derived_experience_level IN ('Beginner', 'Intermediate', 'Advanced')",
            name='check_experience_level'
        ),
        sa.CheckConstraint(
            "software_experience_years >= 0 AND software_experience_years <= 50",
            name='check_software_years'
        ),
        sa.CheckConstraint(
            "hardware_experience_years >= 0 AND hardware_experience_years <= 50",
            name='check_hardware_years'
        )
    )

    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('refresh_token_hash', sa.String(255), nullable=True),
        sa.Column('ip_address', INET, nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('expires_at', sa.TIMESTAMP, nullable=False),
        sa.Column('last_activity_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.Column('revoked', sa.Boolean, server_default='false'),
        sa.CheckConstraint('expires_at > created_at', name='check_expires_after_created')
    )

    # Create tab_preferences table
    op.create_table(
        'tab_preferences',
        sa.Column('user_id', UUID, sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('active_tab', sa.String(20), nullable=False, server_default="'original'"),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint(
            "active_tab IN ('original', 'personalized')",
            name='check_active_tab'
        )
    )

    # Create indexes (see individual table definitions above)
    # ... indexes created here ...

def downgrade():
    op.drop_table('tab_preferences')
    op.drop_table('user_sessions')
    op.drop_table('user_profiles')
    op.drop_table('users')
```

---

## Pydantic Models (Backend)

**User Models**:
```python
from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
import re

class ExperienceLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"

class UserStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"

# Request/Response Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    programming_languages: List[str] = []
    frameworks: List[str] = []
    software_experience_years: int = 0
    robotics_platforms: List[str] = []
    sensors_actuators: List[str] = []
    hardware_experience_years: int = 0

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

    @field_validator('software_experience_years', 'hardware_experience_years')
    @classmethod
    def validate_experience_years(cls, v: int) -> int:
        if v < 0 or v > 50:
            raise ValueError('Experience years must be between 0 and 50')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    status: UserStatus
    created_at: datetime
    last_login_at: Optional[datetime]

class UserProfileResponse(BaseModel):
    user_id: str
    programming_languages: List[str]
    frameworks: List[str]
    software_experience_years: int
    robotics_platforms: List[str]
    sensors_actuators: List[str]
    hardware_experience_years: int
    derived_experience_level: ExperienceLevel
    updated_at: datetime

class UserProfileUpdate(BaseModel):
    programming_languages: Optional[List[str]] = None
    frameworks: Optional[List[str]] = None
    software_experience_years: Optional[int] = None
    robotics_platforms: Optional[List[str]] = None
    sensors_actuators: Optional[List[str]] = None
    hardware_experience_years: Optional[int] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
```

---

## TypeScript Types (Frontend)

**Type Definitions** (`src/types/auth.ts` and `src/types/profile.ts`):
```typescript
// auth.ts
export type UserStatus = 'active' | 'suspended' | 'deleted';

export interface User {
  id: string;
  email: string;
  status: UserStatus;
  createdAt: string;  // ISO 8601 timestamp
  lastLoginAt?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  programmingLanguages?: string[];
  frameworks?: string[];
  softwareExperienceYears?: number;
  roboticsPlatforms?: string[];
  sensorsActuators?: string[];
  hardwareExperienceYears?: number;
}

export interface TokenResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: number;  // seconds
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// profile.ts
export type ExperienceLevel = 'Beginner' | 'Intermediate' | 'Advanced';

export interface UserProfile {
  userId: string;
  programmingLanguages: string[];
  frameworks: string[];
  softwareExperienceYears: number;
  roboticsPlatforms: string[];
  sensorsActuators: string[];
  hardwareExperienceYears: number;
  derivedExperienceLevel: ExperienceLevel;
  updatedAt: string;
}

export interface ProfileUpdateRequest {
  programmingLanguages?: string[];
  frameworks?: string[];
  softwareExperienceYears?: number;
  roboticsPlatforms?: string[];
  sensorsActuators?: string[];
  hardwareExperienceYears?: number;
}

export interface BackgroundOptions {
  programmingLanguages: string[];
  frameworks: string[];
  roboticsPlatforms: string[];
  sensorsActuators: string[];
}
```

---

## Data Integrity & Business Rules

### 1. User Creation
- Email must be unique across all users
- Password must meet strength requirements before storage
- User profile is created atomically with user account (transaction)
- Derived experience level is calculated immediately on signup

### 2. Profile Updates
- Any profile update triggers recalculation of derived experience level
- JSONB arrays are normalized (lowercase) for consistent matching
- Experience years are validated (0-50 range)
- Updated timestamp is auto-updated via database trigger

### 3. Session Management
- Maximum 5 active sessions per user (oldest auto-revoked)
- Expired sessions are cleaned up daily (cron job)
- Session tokens are hashed before storage (never store raw tokens)
- IP and user agent tracked for security auditing

### 4. Content Personalization
- Derived experience level is cached to avoid recalculation on every request
- Content variant selection is purely read-only (no writes during content serving)
- Fallback to 'Beginner' level if calculation fails

---

## Seed Data (Development/Testing)

**Predefined Options** (loaded as constants in application):
```json
{
  "programmingLanguages": [
    "Python", "C++", "Java", "JavaScript", "C", "C#",
    "Rust", "Go", "MATLAB", "Swift", "Kotlin"
  ],
  "frameworks": [
    "ROS 2", "TensorFlow", "PyTorch", "OpenCV", "Unity",
    "Gazebo", "React", "FastAPI", "Django", "Flask"
  ],
  "roboticsPlatforms": [
    "Arduino", "Raspberry Pi", "NVIDIA Jetson", "Intel NUC",
    "Boston Dynamics Spot", "Universal Robots", "ABB Robots"
  ],
  "sensorsActuators": [
    "LiDAR", "Depth Camera", "IMU", "GPS", "Ultrasonic Sensor",
    "Servo Motor", "Stepper Motor", "Gripper", "Force Sensor"
  ]
}
```

**Test Users**:
```sql
-- Beginner user
INSERT INTO users (id, email, password_hash, status)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'beginner@example.com',
  '$2b$12$...',  -- bcrypt hash of "TestPass123"
  'active'
);

INSERT INTO user_profiles (
  user_id, programming_languages, frameworks,
  software_experience_years, robotics_platforms, sensors_actuators,
  hardware_experience_years, derived_experience_level
)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  '["python"]'::jsonb,
  '[]'::jsonb,
  1,
  '["arduino"]'::jsonb,
  '["ultrasonic sensor"]'::jsonb,
  0,
  'Beginner'
);

-- Advanced user
INSERT INTO users (id, email, password_hash, status)
VALUES (
  '00000000-0000-0000-0000-000000000002',
  'advanced@example.com',
  '$2b$12$...',
  'active'
);

INSERT INTO user_profiles (
  user_id, programming_languages, frameworks,
  software_experience_years, robotics_platforms, sensors_actuators,
  hardware_experience_years, derived_experience_level
)
VALUES (
  '00000000-0000-0000-0000-000000000002',
  '["python", "c++", "rust"]'::jsonb,
  '["ros 2", "tensorflow", "pytorch"]'::jsonb,
  8,
  '["nvidia jetson", "universal robots"]'::jsonb,
  '["lidar", "depth camera", "imu", "servo motor"]'::jsonb,
  7,
  'Advanced'
);
```

---

## Performance Considerations

### Indexes Strategy
- **Users**: Index on email (unique), status (filtered), created_at (DESC for recent users)
- **User Profiles**: Index on derived_experience_level (common filter), GIN indexes on JSONB arrays (for contains queries)
- **User Sessions**: Index on user_id (many sessions per user), token_hash (unique lookup), expires_at (cleanup queries)
- **Tab Preferences**: Index on updated_at (analytics)

### Query Optimization
- Use prepared statements for all SQL queries
- Leverage PostgreSQL JSONB operators (`?`, `@>`, `||`) for array operations
- Use connection pooling (psycopg pool) for concurrent requests
- Implement query result caching for predefined options list

### Scalability
- Database supports 100+ concurrent users per spec (SC-010)
- JSONB columns scale well to ~50 items per array
- Session cleanup prevents table bloat
- Consider read replicas if user base exceeds 10,000 active users

---

## Security Considerations

### Data Protection
- Passwords are bcrypt hashed with cost factor 12
- Session tokens are SHA-256 hashed before storage
- No PII in logs or error messages
- Database encryption at rest (Neon Postgres feature)

### Access Control
- All profile queries require authenticated user
- Users can only access/modify their own profile
- Admin role required for user management operations (future)

### SQL Injection Prevention
- All queries use parameterized statements (psycopg3)
- JSONB fields validated at application layer
- Database constraints provide additional validation layer

---

## Next Steps

1. ✅ Data model defined
2. ⏭️ Create Alembic migration files
3. ⏭️ Implement SQLAlchemy ORM models
4. ⏭️ Implement Pydantic request/response models
5. ⏭️ Generate TypeScript types from OpenAPI schemas
6. ⏭️ Write unit tests for experience level calculation
7. ⏭️ Create API contracts (Phase 1: contracts/)

## References

- PostgreSQL Documentation: https://www.postgresql.org/docs/current/
- Alembic Migrations: https://alembic.sqlalchemy.org/
- SQLAlchemy ORM: https://www.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- Neon Postgres: https://neon.tech/docs/
