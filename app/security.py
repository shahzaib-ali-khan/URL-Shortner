from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.config import settings


class PasswordHasher:
    def hash(self, password: str) -> str:
        # Convert password to bytes
        password_bytes = password.encode("utf-8")

        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Return as string
        return hashed.decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        try:
            password_bytes = plain_password.encode("utf-8")
            hashed_bytes = hashed_password.encode("utf-8")
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False


class TokenManager:
    def __init__(
        self,
        secret_key: str = settings.SECRET_KEY,
        algorithm: str = settings.ALGORITHM,
        access_token_expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(
        self, data: dict[str, any], expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> Optional[dict[str, any]]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None


# Create global instances
password_hasher = PasswordHasher()
token_manager = TokenManager()
