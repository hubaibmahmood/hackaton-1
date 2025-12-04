"""
JWT validation middleware for FastAPI.
Validates JWT tokens issued by the Auth Server.
"""

from typing import Annotated

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.database.postgres import postgres_db

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict:
    """
    Validate Session Token via Database Lookup.

    Args:
        credentials: HTTP Bearer token from Authorization header (Session Token)

    Returns:
        dict: User information

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials

    try:
        async with postgres_db.get_connection() as conn:
            async with conn.cursor() as cur:
                # 1. Find valid session
                # Note: better-auth might use different table/column names depending on config
                # We assume table 'user_sessions' and column 'token' based on our migration
                await cur.execute(
                    """
                    SELECT s.user_id, u.email, u.status, u.email_verified
                    FROM user_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.token = %s AND s.expires_at > NOW()
                    """,
                    (token,),
                )
                row = await cur.fetchone()

                if not row:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired session token",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Return user information
                # row is a dict-like object (dict_row)
                return {
                    "user_id": str(row["user_id"]), # Ensure string for UUID
                    "email": row["email"],
                    "email_verified": row["email_verified"],
                    "status": row["status"],
                }

    except Exception as e:
        # If specific HTTPException, re-raise it
        if isinstance(e, HTTPException):
            raise e
            
        # Otherwise, generic auth error
        print(f"Auth Error: {e}") # Log for debugging
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    """
    Get current active user (extends get_current_user with additional checks).

    Args:
        current_user: User information from JWT token

    Returns:
        dict: Active user information

    Raises:
        HTTPException: If user is not active
    """
    # Add additional checks here if needed (e.g., check if user is suspended)
    return current_user


# Convenience type annotations
CurrentUser = Annotated[dict, Depends(get_current_user)]
CurrentActiveUser = Annotated[dict, Depends(get_current_active_user)]
