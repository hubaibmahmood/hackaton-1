/**
 * TypeScript types for authentication flow.
 * Shared types for signup, signin, and session management.
 */

/**
 * Signup request payload.
 * Sent to POST /api/auth/sign-up/email
 */
export interface SignupRequest {
  email: string;
  password: string;
  name?: string; // Optional display name
}

/**
 * Signup response from better-auth.
 * Includes user data and session token.
 */
export interface SignupResponse {
  user: {
    id: string;
    email: string;
    emailVerified: boolean;
    createdAt: string;
    name?: string;
  };
  session: {
    id: string;
    userId: string;
    expiresAt: string;
    token: string;
  };
}

/**
 * Signin request payload.
 * Sent to POST /api/auth/sign-in/email
 */
export interface SigninRequest {
  email: string;
  password: string;
}

/**
 * Signin response from better-auth.
 */
export interface SigninResponse {
  user: {
    id: string;
    email: string;
    emailVerified: boolean;
    name?: string;
  };
  session: {
    id: string;
    userId: string;
    expiresAt: string;
    token: string;
  };
}

/**
 * User session data.
 * Returned by GET /api/auth/me
 */
export interface SessionUser {
  userId: string;
  email: string;
  emailVerified: boolean;
  createdAt: string;
  name?: string;
}

/**
 * Token verification request.
 * Sent to POST /api/auth/verify-token
 */
export interface VerifyTokenRequest {
  token: string;
}

/**
 * Token verification response.
 */
export interface VerifyTokenResponse {
  valid: boolean;
  userId?: string;
  email?: string;
}

/**
 * Error response from auth server.
 */
export interface AuthErrorResponse {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}
