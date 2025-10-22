from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth import get_auth_service, get_current_active_user
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def signup(
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """
    Register a new user with email and password.

    - **email**: Valid email address
    - **password**: Secure password (minimum 8 characters)
    """
    user = await auth_service.register_user(user_data)
    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/login", response_model=Token, summary="Login and get access token")
async def login(
    login_data: UserLogin,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Token:
    """
    Authenticate user and return JWT access token.

    - **email**: Your email address
    - **password**: Your password
    """
    return await auth_service.authenticate_user(login_data)


@router.get("/me", response_model=UserResponse, summary="Get current user information")
async def get_me(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
) -> UserResponse:
    """
    Get information about the currently authenticated user.

    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.post("/logout", status_code=status.HTTP_200_OK, summary="Logout user")
async def logout(
    current_user: Annotated[UserResponse, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    Logout the currently authenticated user.

    Since this is using stateless JWT tokens, the logout is handled client-side
    by deleting the token. This endpoint validates that the token is still valid
    and returns a success message.

    **Client should:**
    - Delete the token from local storage/cookies
    - Remove the Authorization header from future requests
    - Redirect to login page

    Requires valid JWT token in Authorization header.
    """
    return {
        "message": "Successfully logged out",
    }
