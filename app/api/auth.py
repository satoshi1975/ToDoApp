from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, Token
from app.services.auth_service import AuthService, get_auth_service
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", 
    summary="Register new user",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User successfully registered"},
        400: {"description": "Invalid user data"},
        409: {"description": "User with this username already exists"},
        500: {"description": "Internal server error"}
    }
)
async def register(user: UserCreate, auth_service: AuthService = Depends(get_auth_service)) -> Dict[str, Any]:
    """
    Register a new user.
    
    Args:
        user: New user data
        auth_service: Authentication service
        
    Returns:
        Dict[str, Any]: Information about registered user
        
    Raises:
        HTTPException: On registration errors
    """
    try:
        logger.info(f"Attempting to register user: {user.username}")
        result = await auth_service.register(user)
        logger.info(f"User successfully registered: {user.username}")
        return result
    except HTTPException as e:
        logger.warning(f"Error registering user {user.username}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error registering user {user.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while registering user"
        )

@router.post("/token", 
    response_model=Token, 
    summary="Get JWT token",
    responses={
        200: {"description": "Tokens successfully obtained"},
        401: {"description": "Invalid credentials"},
        500: {"description": "Internal server error"}
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    """
    Get JWT tokens for authentication.
    
    Args:
        form_data: Form data with credentials
        auth_service: Authentication service
        
    Returns:
        Token: Access and refresh tokens
        
    Raises:
        HTTPException: On authentication errors
    """
    try:
        logger.info(f"Attempting to login user: {form_data.username}")
        result = await auth_service.login(form_data)
        logger.info(f"User successfully logged in: {form_data.username}")
        return result
    except HTTPException as e:
        logger.warning(f"Error logging in user {form_data.username}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error logging in user {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

@router.post("/refresh", 
    response_model=Token, 
    summary="Refresh access token",
    responses={
        200: {"description": "Tokens successfully refreshed"},
        401: {"description": "Invalid refresh token"},
        500: {"description": "Internal server error"}
    }
)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
) -> Token:
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_token: Refresh token
        auth_service: Authentication service
        
    Returns:
        Token: New access and refresh tokens
        
    Raises:
        HTTPException: On token refresh errors
    """
    try:
        logger.info("Attempting to refresh token")
        result = await auth_service.refresh_token(refresh_token)
        logger.info("Token successfully refreshed")
        return result
    except HTTPException as e:
        logger.warning(f"Error refreshing token: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while refreshing token"
        )

