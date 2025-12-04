import React, { createContext, useState, useEffect } from 'react';
import { User } from '../../types/auth';
import { authService } from '../../services/authService';
import { authClient } from '../../services/authClient';
import { setAccessToken } from '../../services/tokenStore';
import LoadingSpinner from '../common/LoadingSpinner';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  signin: (data: any) => Promise<void>;
  signout: () => Promise<void>;
  checkSession: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkSession = async () => {
    try {
      // Call /api/auth/me endpoint which we verified exists in routes.ts
      const response = await authClient.get('/api/auth/me');
      setUser(response.data);
      if (response.data.id) { // Check if session ID exists in the response
        setAccessToken(response.data.id); // Store the session ID
      }
    } catch (error) {
      // Session invalid or expired
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkSession();
  }, []);

  const signin = async (data: any) => {
    await authService.signin(data);
    // After signin, fetch user details
    await checkSession();
  };

  const signout = async () => {
    await authService.signout();
    setUser(null);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, signin, signout, checkSession }}>
      {children}
    </AuthContext.Provider>
  );
};
