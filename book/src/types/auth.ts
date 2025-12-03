/**
 * Authentication type definitions for frontend.
 * Defines interfaces for auth requests and responses.
 */

export interface User {
  id: string;
  email: string;
  emailVerified: boolean;
  createdAt: string;
}

export interface SignupRequest {
  email: string;
  password: string;
}

export interface SignupResponse {
  user: User;
  session: {
    id: string;
    userId: string;
    expiresAt: string;
    token: string;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface TokenResponse {
  accessToken: string;
  refreshToken?: string;
  expiresIn: number;
  tokenType: string;
}

export interface AuthResponse {
  user: User;
  token: TokenResponse;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface VerifyTokenResponse {
  valid: boolean;
  userId: string;
  email: string;
}

export type AuthError = {
  message: string;
  statusCode: number;
  errors?: Record<string, string[]>;
};
