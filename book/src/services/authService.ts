import { authClient } from './authClient';
import { SignupRequest, LoginRequest } from '../types/auth';
import { setAccessToken } from './tokenStore';

export const authService = {
  signup: async (data: SignupRequest) => {
    // Using better-auth standard email signup endpoint
    const response = await authClient.post('/api/auth/sign-up/email', {
      email: data.email,
      password: data.password
    });
    
    if (response.data.token) {
        setAccessToken(response.data.token);
    }
    return response.data;
  },

  signin: async (data: LoginRequest) => {
    const response = await authClient.post('/api/auth/signin', {
        email: data.email,
        password: data.password,
        rememberMe: data.rememberMe
    });
    
    if (response.data.token) {
        setAccessToken(response.data.token);
    }
    return response.data;
  },

  signout: async () => {
    try {
        await authClient.post('/api/auth/signout');
    } finally {
        setAccessToken(null);
    }
  },
  
  refresh: async () => {
      // Try to refresh session
      const response = await authClient.post('/api/auth/refresh');
      if (response.data.token) {
          setAccessToken(response.data.token);
      }
      return response.data;
  }
};
