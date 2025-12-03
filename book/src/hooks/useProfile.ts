/**
 * Custom hook for user profile management.
 * Handles profile creation and updates.
 */
import { useState } from 'react';
import { apiClient } from '../services/apiClient';
import type { ProfileCreateRequest, ProfileResponse } from '../types/profile';

interface UseProfileReturn {
  createProfile: (profileData: Omit<ProfileCreateRequest, 'user_id'>) => Promise<ProfileResponse>;
  loading: boolean;
  error: string | null;
  clearError: () => void;
}

export function useProfile(userId: string): UseProfileReturn {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createProfile = async (
    profileData: Omit<ProfileCreateRequest, 'user_id'>
  ): Promise<ProfileResponse> => {
    setLoading(true);
    setError(null);

    try {
      const requestData: ProfileCreateRequest = {
        user_id: userId,
        ...profileData,
      };

      const response = await apiClient.post<ProfileResponse>('/api/profile', requestData);
      return response.data;
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Failed to create profile. Please try again.';

      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const clearError = () => setError(null);

  return { createProfile, loading, error, clearError };
}
