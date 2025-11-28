"""API dependencies."""
from typing import Generator, Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is disabled",
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    return current_user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if credentials is None:
        return None

    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None


def require_role(required_roles):
    """
    权限检查装饰器工厂：检查用户是否拥有指定的角色。

    Args:
        required_roles: 允许访问的角色(s)。可以是字符串或字符串列表，如 'admin' 或 ['admin']

    Returns:
        一个依赖函数，用于 FastAPI 路由

    Raises:
        HTTPException: 如果用户没有所需的角色
    """
    # 将 required_roles 转换为列表(如果是字符串)
    if isinstance(required_roles, str):
        roles_list = [required_roles]
    else:
        roles_list = required_roles

    # 将所有角色转换为大写
    roles_list = [role.upper() for role in roles_list]

    async def check_role(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role = current_user.role.value.upper()
        if user_role not in roles_list:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {', '.join(roles_list)}",
            )
        return current_user

    return check_role
