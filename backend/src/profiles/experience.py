"""
Experience level calculation logic.
Implements conservative matching algorithm based on software/hardware experience.
"""
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience level taxonomy."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


def calculate_experience_level(
    software_years: int,
    hardware_years: int
) -> ExperienceLevel:
    """
    Calculate derived experience level using conservative matching.

    Returns the LOWER of software and hardware experience levels
    to ensure content remains accessible (Zone of Proximal Development).

    Rules:
    - Beginner: 0-1 years
    - Intermediate: 2-4 years
    - Advanced: 5+ years

    Args:
        software_years: Years of software experience (0-50)
        hardware_years: Years of hardware experience (0-50)

    Returns:
        ExperienceLevel: Derived experience level (minimum of both domains)

    Examples:
        >>> calculate_experience_level(6, 1)
        ExperienceLevel.BEGINNER  # Advanced + Beginner = Beginner

        >>> calculate_experience_level(3, 4)
        ExperienceLevel.INTERMEDIATE  # Intermediate + Intermediate

        >>> calculate_experience_level(7, 8)
        ExperienceLevel.ADVANCED  # Advanced + Advanced
    """

    def years_to_level(years: int) -> ExperienceLevel:
        """Convert years of experience to experience level."""
        if years >= 5:
            return ExperienceLevel.ADVANCED
        elif years >= 2:
            return ExperienceLevel.INTERMEDIATE
        else:
            return ExperienceLevel.BEGINNER

    software_level = years_to_level(software_years)
    hardware_level = years_to_level(hardware_years)

    # Return minimum level (most conservative)
    level_order = [
        ExperienceLevel.BEGINNER,
        ExperienceLevel.INTERMEDIATE,
        ExperienceLevel.ADVANCED,
    ]

    software_idx = level_order.index(software_level)
    hardware_idx = level_order.index(hardware_level)

    return level_order[min(software_idx, hardware_idx)]


# Convenience function for string output
def calculate_experience_level_str(software_years: int, hardware_years: int) -> str:
    """
    Calculate experience level and return as string.

    Args:
        software_years: Years of software experience
        hardware_years: Years of hardware experience

    Returns:
        str: Experience level as string ("Beginner", "Intermediate", or "Advanced")
    """
    return calculate_experience_level(software_years, hardware_years).value
