/**
 * Profile type definitions for frontend.
 * Defines interfaces for user profiles and background information.
 */

export type ExperienceLevel = 'Beginner' | 'Intermediate' | 'Advanced';

export interface BackgroundOptions {
  programmingLanguages: string[];
  frameworks: string[];
  roboticsPlatforms: string[];
  sensorsActuators: string[];
}

export interface UserProfile {
  userId: string;
  programmingLanguages: string[];
  frameworks: string[];
  softwareExperienceYears: number;
  roboticsPlatforms: string[];
  sensorsActuators: string[];
  hardwareExperienceYears: number;
  derivedExperienceLevel: ExperienceLevel;
  createdAt: string;
  updatedAt: string;
}

export interface CreateProfileRequest {
  userId: string;
  programmingLanguages: string[];
  frameworks: string[];
  softwareExperienceYears: number;
  roboticsPlatforms: string[];
  sensorsActuators: string[];
  hardwareExperienceYears: number;
}

export interface UpdateProfileRequest {
  programmingLanguages?: string[];
  frameworks?: string[];
  softwareExperienceYears?: number;
  roboticsPlatforms?: string[];
  sensorsActuators?: string[];
  hardwareExperienceYears?: number;
}

export interface TabPreference {
  userId: string;
  activeTab: 'original' | 'personalized';
  updatedAt: string;
}

export interface ProfileState {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
}
