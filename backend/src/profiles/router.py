"""
Profile management API endpoints.
Handles profile creation, retrieval, and updates.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_user
from src.profiles.models import UserProfileCreate, UserProfileUpdate, UserProfileResponse
from src.profiles.service import create_profile, get_profile, update_profile
from src.utils.errors import NotFoundError, ConflictError
from src.utils.logger import logger


router = APIRouter()


@router.post(
    "/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user profile",
    description="Create a new user profile with background information and experience levels."
)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new user profile.

    Args:
        profile_data: Profile creation data
        current_user: Authenticated user from JWT token

    Returns:
        UserProfileResponse: Created profile with derived experience level

    Raises:
        409 Conflict: Profile already exists for user
    """
    # Ensure profile is being created for the authenticated user
    if profile_data.user_id != current_user["user_id"]:
        logger.warning(
            f"User {current_user['user_id']} attempted to create profile for {profile_data.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create profile for another user"
        )

    try:
        profile = await create_profile(profile_data)
        logger.info(f"Profile created successfully for user {current_user['user_id']}")
        return profile
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    summary="Get user profile",
    description="Retrieve the authenticated user's profile."
)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get the authenticated user's profile.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        UserProfileResponse: User profile

    Raises:
        404 Not Found: Profile doesn't exist
    """
    user_id = current_user["user_id"]
    profile = await get_profile(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found for user {user_id}"
        )

    return profile


@router.put(
    "/profile",
    response_model=UserProfileResponse,
    summary="Update user profile",
    description="Update the authenticated user's profile (partial updates allowed)."
)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update the authenticated user's profile.

    Args:
        profile_data: Profile update data (partial)
        current_user: Authenticated user from JWT token

    Returns:
        UserProfileResponse: Updated profile with recalculated experience level

    Raises:
        404 Not Found: Profile doesn't exist
    """
    user_id = current_user["user_id"]

    try:
        profile = await update_profile(user_id, profile_data)
        logger.info(f"Profile updated successfully for user {user_id}")
        return profile
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
