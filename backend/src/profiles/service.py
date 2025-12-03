"""
Profile service layer.
Handles profile creation, updates, and experience level calculation.
"""
import json
from datetime import datetime
from typing import Optional

from src.database.init import get_db_connection
from src.profiles.models import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from src.profiles.experience import calculate_experience_level_str
from src.utils.errors import NotFoundError, ConflictError
from src.utils.logger import logger


async def create_profile(profile_data: UserProfileCreate) -> UserProfileResponse:
    """
    Create a new user profile with derived experience level.

    Args:
        profile_data: Profile creation data

    Returns:
        UserProfileResponse: Created profile

    Raises:
        ConflictError: If profile already exists for user
    """
    # Calculate derived experience level
    derived_level = calculate_experience_level_str(
        profile_data.software_experience_years,
        profile_data.hardware_experience_years
    )

    logger.info(
        f"Creating profile for user {profile_data.user_id}",
        {"derived_level": derived_level}
    )

    async with get_db_connection() as conn:
        # Check if profile already exists
        existing = await conn.fetchone(
            "SELECT user_id FROM user_profiles WHERE user_id = %s",
            (profile_data.user_id,)
        )

        if existing:
            raise ConflictError(f"Profile already exists for user {profile_data.user_id}")

        # Insert profile
        await conn.execute(
            """
            INSERT INTO user_profiles (
                user_id,
                programming_languages,
                frameworks,
                software_experience_years,
                robotics_platforms,
                sensors_actuators,
                hardware_experience_years,
                derived_experience_level,
                created_at,
                updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                profile_data.user_id,
                json.dumps(profile_data.programming_languages),
                json.dumps(profile_data.frameworks),
                profile_data.software_experience_years,
                json.dumps(profile_data.robotics_platforms),
                json.dumps(profile_data.sensors_actuators),
                profile_data.hardware_experience_years,
                derived_level,
                datetime.utcnow(),
                datetime.utcnow(),
            )
        )

        await conn.commit()

        # Fetch created profile
        row = await conn.fetchone(
            """
            SELECT
                user_id,
                programming_languages,
                frameworks,
                software_experience_years,
                robotics_platforms,
                sensors_actuators,
                hardware_experience_years,
                derived_experience_level,
                created_at,
                updated_at
            FROM user_profiles
            WHERE user_id = %s
            """,
            (profile_data.user_id,)
        )

    logger.info(f"Profile created for user {profile_data.user_id}")

    return UserProfileResponse(
        user_id=row["user_id"],
        programming_languages=row["programming_languages"],
        frameworks=row["frameworks"],
        software_experience_years=row["software_experience_years"],
        robotics_platforms=row["robotics_platforms"],
        sensors_actuators=row["sensors_actuators"],
        hardware_experience_years=row["hardware_experience_years"],
        derived_experience_level=row["derived_experience_level"],
        created_at=row["created_at"].isoformat(),
        updated_at=row["updated_at"].isoformat(),
    )


async def get_profile(user_id: str) -> Optional[UserProfileResponse]:
    """
    Get user profile by user ID.

    Args:
        user_id: User ID

    Returns:
        UserProfileResponse: User profile or None if not found
    """
    async with get_db_connection() as conn:
        row = await conn.fetchone(
            """
            SELECT
                user_id,
                programming_languages,
                frameworks,
                software_experience_years,
                robotics_platforms,
                sensors_actuators,
                hardware_experience_years,
                derived_experience_level,
                created_at,
                updated_at
            FROM user_profiles
            WHERE user_id = %s
            """,
            (user_id,)
        )

    if not row:
        return None

    return UserProfileResponse(
        user_id=row["user_id"],
        programming_languages=row["programming_languages"],
        frameworks=row["frameworks"],
        software_experience_years=row["software_experience_years"],
        robotics_platforms=row["robotics_platforms"],
        sensors_actuators=row["sensors_actuators"],
        hardware_experience_years=row["hardware_experience_years"],
        derived_experience_level=row["derived_experience_level"],
        created_at=row["created_at"].isoformat(),
        updated_at=row["updated_at"].isoformat(),
    )


async def update_profile(user_id: str, profile_data: UserProfileUpdate) -> UserProfileResponse:
    """
    Update user profile and recalculate derived experience level.

    Args:
        user_id: User ID
        profile_data: Profile update data (partial)

    Returns:
        UserProfileResponse: Updated profile

    Raises:
        NotFoundError: If profile doesn't exist
    """
    async with get_db_connection() as conn:
        # Get current profile
        current = await conn.fetchone(
            """
            SELECT
                software_experience_years,
                hardware_experience_years,
                programming_languages,
                frameworks,
                robotics_platforms,
                sensors_actuators
            FROM user_profiles
            WHERE user_id = %s
            """,
            (user_id,)
        )

        if not current:
            raise NotFoundError(f"Profile not found for user {user_id}")

        # Merge updates with current values
        software_years = profile_data.software_experience_years if profile_data.software_experience_years is not None else current["software_experience_years"]
        hardware_years = profile_data.hardware_experience_years if profile_data.hardware_experience_years is not None else current["hardware_experience_years"]

        # Recalculate derived level
        derived_level = calculate_experience_level_str(software_years, hardware_years)

        # Build update fields
        update_fields = []
        update_values = []

        if profile_data.programming_languages is not None:
            update_fields.append("programming_languages = %s")
            update_values.append(json.dumps(profile_data.programming_languages))

        if profile_data.frameworks is not None:
            update_fields.append("frameworks = %s")
            update_values.append(json.dumps(profile_data.frameworks))

        if profile_data.software_experience_years is not None:
            update_fields.append("software_experience_years = %s")
            update_values.append(profile_data.software_experience_years)

        if profile_data.robotics_platforms is not None:
            update_fields.append("robotics_platforms = %s")
            update_values.append(json.dumps(profile_data.robotics_platforms))

        if profile_data.sensors_actuators is not None:
            update_fields.append("sensors_actuators = %s")
            update_values.append(json.dumps(profile_data.sensors_actuators))

        if profile_data.hardware_experience_years is not None:
            update_fields.append("hardware_experience_years = %s")
            update_values.append(profile_data.hardware_experience_years)

        # Always update derived level and updated_at
        update_fields.append("derived_experience_level = %s")
        update_values.append(derived_level)

        update_fields.append("updated_at = %s")
        update_values.append(datetime.utcnow())

        # Add user_id for WHERE clause
        update_values.append(user_id)

        # Execute update
        await conn.execute(
            f"""
            UPDATE user_profiles
            SET {', '.join(update_fields)}
            WHERE user_id = %s
            """,
            tuple(update_values)
        )

        await conn.commit()

    logger.info(f"Profile updated for user {user_id}", {"new_derived_level": derived_level})

    # Return updated profile
    return await get_profile(user_id)
