# API Schemas

This directory contains shared schema definitions used across authentication and profile management APIs.

## Purpose

These schemas serve as the **single source of truth** for data structures exchanged between frontend and backend. They enable:

1. **Contract-First Development**: Define data contracts before implementation
2. **Type Generation**: Generate Pydantic models (Python) and TypeScript types from OpenAPI schemas
3. **Validation**: Ensure consistent validation rules across client and server
4. **Documentation**: Auto-generate API documentation with accurate examples

## Schema Organization

### `common.yaml`
Shared schemas used by both `auth-api.yaml` and `profile-api.yaml`:
- `ErrorResponse` - Standard error format
- `ExperienceLevel` - Enum for experience taxonomy
- `BackgroundArrays` - Reusable array types for multi-valued fields

### Parent API Specs
Complete API specifications with endpoints:
- `../auth-api.yaml` - Authentication endpoints (signup, signin, signout, refresh, verify)
- `../profile-api.yaml` - Profile management endpoints (get, update, options, tab preference)

## Usage

### Backend (Pydantic Models)

Generate Python models from OpenAPI schemas:

```bash
# Install openapi-python-client
pip install openapi-python-client

# Generate from auth-api.yaml
openapi-python-client generate --path contracts/auth-api.yaml --output-path backend/src/auth/generated

# Generate from profile-api.yaml
openapi-python-client generate --path contracts/profile-api.yaml --output-path backend/src/profiles/generated
```

Or manually implement Pydantic models matching schema definitions:

```python
# backend/src/auth/models.py
from pydantic import BaseModel, EmailStr, field_validator
from typing import List
import re

class SignupRequest(BaseModel):
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
```

### Frontend (TypeScript Types)

Generate TypeScript types from OpenAPI schemas:

```bash
# Install openapi-typescript
npm install --save-dev openapi-typescript

# Generate from auth-api.yaml
npx openapi-typescript contracts/auth-api.yaml --output book/src/types/auth.generated.ts

# Generate from profile-api.yaml
npx openapi-typescript contracts/profile-api.yaml --output book/src/types/profile.generated.ts
```

Or manually create TypeScript types matching schema definitions:

```typescript
// book/src/types/auth.ts
export type ExperienceLevel = 'Beginner' | 'Intermediate' | 'Advanced';

export interface SignupRequest {
  email: string;
  password: string;
  programmingLanguages?: string[];
  frameworks?: string[];
  softwareExperienceYears: number;
  roboticsPlatforms?: string[];
  sensorsActuators?: string[];
  hardwareExperienceYears: number;
}

export interface AuthResponse {
  userId: string;
  email: string;
  derivedExperienceLevel: ExperienceLevel;
  sessionToken: string;
  expiresAt: string;
}
```

## Validation Rules

All schemas enforce validation rules from the specification:

### Password (NFR-001)
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

### Experience Years
- Range: 0-50 years
- Integer only

### Email
- Valid email format (RFC 5322)
- Maximum 255 characters

### Arrays
- Empty arrays allowed (default: `[]`)
- Each item is a non-empty string
- Support predefined options + "Other" for custom input

## Contract Testing

Validate backend responses against OpenAPI schemas:

```python
# backend/tests/test_auth_contract.py
import pytest
from openapi_core import OpenAPI
from openapi_core.validation.response import V30ResponseValidator

@pytest.fixture
def openapi_spec():
    return OpenAPI.from_file_path('contracts/auth-api.yaml')

def test_signup_response_matches_schema(client, openapi_spec):
    response = client.post('/auth/signup', json={
        'email': 'test@example.com',
        'password': 'SecurePass123',
        'softwareExperienceYears': 2,
        'hardwareExperienceYears': 1
    })

    validator = V30ResponseValidator(openapi_spec)
    result = validator.validate(response)
    assert result.errors == []
```

## Schema Evolution

When updating schemas:

1. **Add new optional fields** - Backward compatible
2. **Deprecate fields** - Mark with `deprecated: true` in schema
3. **Remove fields** - Increment API version (breaking change)
4. **Change validation** - Document in migration guide

Example deprecation:

```yaml
properties:
  oldField:
    type: string
    deprecated: true
    description: "DEPRECATED: Use newField instead. Will be removed in v2.0"
  newField:
    type: string
```

## References

- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [openapi-typescript](https://github.com/drwpow/openapi-typescript)
- [openapi-python-client](https://github.com/openapi-generators/openapi-python-client)
