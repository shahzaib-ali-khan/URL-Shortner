from typing import Optional

from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import Token, UserCreate, UserLogin
from app.security import password_hasher, token_manager


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_manager = token_manager

    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create new user
        hashed_password = self.password_hasher.hash(user_data.password)
        user = User(email=user_data.email, hashed_password=hashed_password)

        return await self.user_repository.create(user)

    async def authenticate_user(self, login_data: UserLogin) -> Token:
        # Get user by username
        user = await self.user_repository.get_by_email(login_data.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not self.password_hasher.verify(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        # Create access token
        access_token = self.token_manager.create_access_token(data={"sub": user.email})

        return Token(access_token=access_token)

    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        payload = self.token_manager.decode_token(token)
        if payload is None:
            raise credentials_exception

        email: Optional[str] = payload.get("sub")
        if email is None:
            raise credentials_exception

        user = await self.user_repository.get_by_email(email)
        if user is None:
            raise credentials_exception

        return user
