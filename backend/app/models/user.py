"""User models."""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Table, Enum
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserRole(str, PyEnum):
    """用户角色枚举."""
    ADMIN = "ADMIN"          # 管理员
    VIP = "VIP"              # VIP付费用户
    NORMAL = "NORMAL"        # 普通用户


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    avatar_url = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.NORMAL, nullable=False)  # 用户角色
    status = Column(String(20), default="active")  # active, disabled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime)

    # Relationships
    subscriptions = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="[Subscription.user_id]"
    )
