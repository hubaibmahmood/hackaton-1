import { apiClient } from './apiClient';
import { UserProfile } from '../types/profile';

export const profileService = {
  createProfile: async (data: any) => {
    const response = await apiClient.post<UserProfile>('/api/profile', data);
    return response.data;
  },
  
  getProfile: async () => {
    const response = await apiClient.get<UserProfile>('/api/profile');
    return response.data;
  },
  
  updateProfile: async (data: Partial<UserProfile>) => {
    const response = await apiClient.put<UserProfile>('/api/profile', data);
    return response.data;
  }
};
