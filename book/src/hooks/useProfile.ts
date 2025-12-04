import { useState, useEffect, useCallback } from 'react';
import { profileService } from '../services/profileService';
import { UserProfile, UpdateProfileRequest } from '../types/profile';
import { useAuth } from './useAuth';

interface ProfileState {
  data: UserProfile | null;
  isLoading: boolean;
  error: string | null;
}

export const useProfile = () => {
  const { user } = useAuth();
  const [profileState, setProfileState] = useState<ProfileState>({
    data: null,
    isLoading: true,
    error: null,
  });

  const fetchProfile = useCallback(async () => {
    if (!user) {
      setProfileState(prev => ({ ...prev, isLoading: false, data: null }));
      return;
    }

    try {
      setProfileState(prev => ({ ...prev, isLoading: true, error: null }));
      const data = await profileService.getProfile();
      setProfileState({ data, isLoading: false, error: null });
    } catch (err: any) {
      // If 404 (Not Found), it just means user has no profile yet. This is expected for new users.
      const isNotFound = err.response?.status === 404;
      setProfileState({
        data: null,
        isLoading: false,
        error: isNotFound ? null : (err.response?.data?.message || 'Failed to load profile'),
      });
    }
  }, [user]);

  const updateProfile = async (data: UpdateProfileRequest) => {
    try {
      setProfileState(prev => ({ ...prev, isLoading: true, error: null }));
      const updatedProfile = await profileService.updateProfile(data);
      setProfileState({ data: updatedProfile, isLoading: false, error: null });
      return updatedProfile;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to update profile';
      setProfileState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw new Error(errorMessage);
    }
  };

  const createProfile = async (data: any) => {
    try {
      setProfileState(prev => ({ ...prev, isLoading: true, error: null }));
      const newProfile = await profileService.createProfile(data);
      setProfileState({ data: newProfile, isLoading: false, error: null });
      return newProfile;
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Failed to create profile';
      setProfileState(prev => ({
        ...prev,
        isLoading: false,
        error: errorMessage,
      }));
      throw new Error(errorMessage);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  return {
    ...profileState,
    fetchProfile,
    updateProfile,
    createProfile,
  };
};