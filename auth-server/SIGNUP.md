# Authentication Signup Flow

This document describes the signup endpoints and flow for user registration.

## Endpoints

### POST /api/auth/sign-up/email

Create a new user account with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Validation Requirements:**
- Email: Valid email format, max 255 characters
- Password:
  - Minimum 8 characters
  - Maximum 128 characters
  - At least one uppercase letter (A-Z)
  - At least one lowercase letter (a-z)
  - At least one number (0-9)

**Response (201 Created):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "emailVerified": false,
    "createdAt": "2025-12-02T10:30:00.000Z"
  },
  "session": {
    "id": "session-id",
    "userId": "550e8400-e29b-41d4-a716-446655440000",
    "expiresAt": "2025-12-09T10:30:00.000Z",
    "token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

**Error Responses:**

- **400 Bad Request** - Invalid input
  ```json
  {
    "error": "Bad Request",
    "message": "Invalid email or password",
    "details": {
      "email": "Invalid email format",
      "password": "Password must be at least 8 characters"
    }
  }
  ```

- **409 Conflict** - User already exists
  ```json
  {
    "error": "Conflict",
    "message": "User with this email already exists"
  }
  ```

- **429 Too Many Requests** - Rate limit exceeded
  ```json
  {
    "error": "Too Many Requests",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
  ```

## Authentication Flow

### 1. User Registration (Signup)

```typescript
// Frontend code example
import { authClient } from './services/authClient';

async function signup(email: string, password: string) {
  try {
    const response = await authClient.post('/api/auth/sign-up/email', {
      email,
      password,
    });

    // Store session token (httpOnly cookie is set automatically)
    const { user, session } = response.data;
    localStorage.setItem('authToken', session.token);

    return { user, session };
  } catch (error) {
    if (error.response?.status === 409) {
      throw new Error('Email already in use');
    }
    throw error;
  }
}
```

### 2. Profile Creation (After Signup)

After successful signup, the user should complete their profile:

```typescript
import { apiClient } from './services/apiClient';

async function createProfile(profileData: {
  programming_languages: string[];
  frameworks: string[];
  software_experience_years: number;
  robotics_platforms: string[];
  sensors_actuators: string[];
  hardware_experience_years: number;
}) {
  // apiClient automatically includes JWT token in Authorization header
  const response = await apiClient.post('/api/profile', {
    user_id: userId, // From signup response
    ...profileData,
  });

  return response.data;
}
```

## Security Features

### Password Hashing
- Passwords are automatically hashed using **bcrypt** by better-auth
- Passwords are never stored in plain text
- Minimum work factor: 10 rounds

### Session Management
- Sessions expire after **7 days**
- Session tokens are stored in **httpOnly cookies** (XSS protection)
- Cookies are marked **Secure** in production (HTTPS only)
- **SameSite=Strict** cookie attribute (CSRF protection)

### Rate Limiting
- **10 requests per minute** per IP address for signup endpoint
- Prevents brute force attacks and spam registrations

### Email Verification
- Email verification is **required in production**
- Verification emails are sent automatically after signup
- Users cannot access protected resources until verified (production only)

## Frontend Integration

### 1. Install Dependencies

```bash
npm install axios @better-auth/react
```

### 2. Create Auth Client

```typescript
// src/services/authClient.ts
import axios from 'axios';

export const authClient = axios.create({
  baseURL: process.env.AUTH_SERVER_URL || 'https://your-auth-server.vercel.app',
  withCredentials: true, // Send cookies
});
```

### 3. Create Signup Hook

```typescript
// src/hooks/useSignup.ts
import { useState } from 'react';
import { authClient } from '../services/authClient';

export function useSignup() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const signup = async (email: string, password: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await authClient.post('/api/auth/sign-up/email', {
        email,
        password,
      });

      localStorage.setItem('authToken', response.data.session.token);
      return response.data;
    } catch (err: any) {
      const message = err.response?.data?.message || 'Signup failed';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { signup, loading, error };
}
```

## Testing

### Manual Testing with curl

```bash
# Signup
curl -X POST http://localhost:3001/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# Get current user
curl -X GET http://localhost:3001/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Unit Testing

See `auth-server/tests/signup.test.ts` for comprehensive test cases.

## Troubleshooting

### "Email already exists" Error
- User has already registered with this email
- Check if user needs to sign in instead of sign up

### "Password validation failed" Error
- Password doesn't meet strength requirements
- Show validation errors to user before submission

### "Rate limit exceeded" Error
- Too many signup attempts from same IP
- Wait 60 seconds before retrying
- Consider implementing CAPTCHA for production

## Related Documentation

- [Authentication Configuration](./src/auth/auth.config.ts)
- [Validation Utilities](./src/auth/validation.ts)
- [API Types](./src/auth/types.ts)
- [Profile Creation](../backend/src/profiles/README.md)
