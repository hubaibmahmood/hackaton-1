"""
Pydantic models for user profiles.
Validates profile creation and update requests.
"""
from typing import List, Optional
from pydantic import BaseModel, field_validator


class UserProfileCreate(BaseModel):
    """User profile creation request model."""

    user_id: str
    programming_languages: List[str] = []
    frameworks: List[str] = []
    software_experience_years: int
    robotics_platforms: List[str] = []
    sensors_actuators: List[str] = []
    hardware_experience_years: int

    @field_validator('software_experience_years', 'hardware_experience_years')
    @classmethod
    def validate_experience_years(cls, v: int) -> int:
        """Validate experience years are within valid range (0-50)."""
        if v < 0:
            raise ValueError('Experience years cannot be negative')
        if v > 50:
            raise ValueError('Experience years cannot exceed 50')
        return v

    @field_validator('programming_languages', 'frameworks', 'robotics_platforms', 'sensors_actuators')
    @classmethod
    def validate_array_items(cls, v: List[str]) -> List[str]:
        """Validate array items are non-empty strings."""
        if v is None:
            return []
        for item in v:
            if not item or not item.strip():
                raise ValueError('Array items must be non-empty strings')
        return [item.strip() for item in v]


class UserProfileUpdate(BaseModel):
    """User profile update request model (partial updates allowed)."""

    programming_languages: Optional[List[str]] = None
    frameworks: Optional[List[str]] = None
    software_experience_years: Optional[int] = None
    robotics_platforms: Optional[List[str]] = None
    sensors_actuators: Optional[List[str]] = None
    hardware_experience_years: Optional[int] = None

    @field_validator('software_experience_years', 'hardware_experience_years')
    @classmethod
    def validate_experience_years(cls, v: Optional[int]) -> Optional[int]:
        """Validate experience years are within valid range (0-50)."""
        if v is not None:
            if v < 0:
                raise ValueError('Experience years cannot be negative')
            if v > 50:
                raise ValueError('Experience years cannot exceed 50')
        return v


class UserProfileResponse(BaseModel):
    """User profile response model."""

    user_id: str
    programming_languages: List[str]
    frameworks: List[str]
    software_experience_years: int
    robotics_platforms: List[str]
    sensors_actuators: List[str]
    hardware_experience_years: int
    derived_experience_level: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
