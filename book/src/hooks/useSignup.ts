/**
 * Custom hook for user signup.
 * Handles signup API calls and state management.
 */
import { useState } from 'react';
import { authClient } from '../services/authClient';
import type { SignupRequest, SignupResponse } from '../types/auth';

interface UseSignupReturn {
  signup: (email: string, password: string) => Promise<SignupResponse>;
  loading: boolean;
  error: string | null;
  clearError: () => void;
}

export function useSignup(): UseSignupReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const signup = async (email: string, password: string): Promise<SignupResponse> => {
    setLoading(true);
    setError(null);

    try {
      const requestData: SignupRequest = { email, password };
      const response = await authClient.post<SignupResponse>(
        '/api/auth/sign-up/email',
        requestData
      );

      // Store session token for API server requests
      if (response.data.session?.token) {
        localStorage.setItem('authToken', response.data.session.token);
      }

      return response.data;
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.message ||
        err.response?.data?.error ||
        'Signup failed. Please try again.';

      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => setError(null);

  return { signup, loading, error, clearError };
}
