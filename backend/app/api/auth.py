"""Authentication API."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.user import (
    LoginRequest,
    RefreshTokenRequest,
    Token,
    UserCreate,
    UserResponse,
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """User login."""
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled",
        )

    # Update last login time
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role.value,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token."""
    payload = decode_token(request.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()

    if not user or user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        role=user.role.value,
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """User logout."""
    # In a more complete implementation, you would blacklist the token
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        status=current_user.status,
        created_at=current_user.created_at,
        role=current_user.role.value,
    )


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user (for development only)."""
    # Check if user exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user with default role "normal"
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=UserRole.NORMAL,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        phone=user.phone,
        avatar_url=user.avatar_url,
        status=user.status,
        created_at=user.created_at,
        role=user.role.value,
    )
