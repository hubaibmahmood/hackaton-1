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

// Backend API types (snake_case naming)
export interface ProfileCreateRequest {
  user_id: string;
  programming_languages: string[];
  frameworks: string[];
  software_experience_years: number;
  robotics_platforms: string[];
  sensors_actuators: string[];
  hardware_experience_years: number;
}

export interface ProfileResponse {
  user_id: string;
  programming_languages: string[];
  frameworks: string[];
  software_experience_years: number;
  robotics_platforms: string[];
  sensors_actuators: string[];
  hardware_experience_years: number;
  derived_experience_level: ExperienceLevel;
  created_at: string;
  updated_at: string;
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
