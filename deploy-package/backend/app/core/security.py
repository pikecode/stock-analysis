"""Security utilities for authentication."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    import hashlib

    # Handle SHA256 fallback hashes
    if len(hashed_password) == 64 and all(c in '0123456789abcdef' for c in hashed_password.lower()):
        plain_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return plain_hash == hashed_password

    # Truncate password to 72 bytes (bcrypt limit)
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]

    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Fallback: try SHA256 comparison
        plain_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return plain_hash == hashed_password


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    import hashlib

    # Truncate password to 72 bytes (bcrypt limit)
    if len(password.encode('utf-8')) > 72:
        password = password[:72]

    try:
        return pwd_context.hash(password)
    except Exception:
        # Fallback: use SHA256 if bcrypt fails
        return hashlib.sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
