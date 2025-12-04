/**
 * Custom hook for user signup.
 * Handles signup API calls and state management.
 */
import { useState } from 'react';
import { authClient } from '../services/authClient';
import { setAccessToken } from '../services/tokenStore';
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

      console.log('Signup response data:', response.data);

      // Check for token in session object OR top-level property (depending on better-auth version/config)
      let sessionToken = response.data.session?.token || response.data.token;

      // If no token in signup response (maybe strictly cookie mode or autoSignIn off), try explicit login
      if (!sessionToken) {
        console.log('No session token in signup response, attempting auto-login...');
        try {
          const loginResponse = await authClient.post<SignupResponse>('/api/auth/sign-in/email', {
            email,
            password,
          });
          sessionToken = loginResponse.data?.session?.token || loginResponse.data?.token;
          console.log('Login response token:', sessionToken ? 'Found' : 'Missing');
        } catch (loginErr) {
          console.error('Auto-login failed:', loginErr);
          // Don't throw here, return the signup response (user created)
          // User will have to login manually
        }
      }

      // Store session token for API server requests
      if (sessionToken) {
        console.log('Saving token:', sessionToken);
        setAccessToken(sessionToken);
      } else {
        console.warn('No session token found after signup/login');
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
