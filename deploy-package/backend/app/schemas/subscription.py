"""Subscription and Plan schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class PlanBase(BaseModel):
    """Base plan schema."""

    name: str
    display_name: str
    description: Optional[str] = None
    price: Decimal
    original_price: Optional[Decimal] = None
    duration_days: int
    features: Optional[str] = None  # JSON string
    is_active: bool = True
    sort_order: int = 0


class PlanCreate(PlanBase):
    """Plan creation schema."""

    pass


class PlanUpdate(BaseModel):
    """Plan update schema."""

    display_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    original_price: Optional[Decimal] = None
    duration_days: Optional[int] = None
    features: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class PlanResponse(PlanBase):
    """Plan response schema."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    """Base subscription schema."""

    user_id: int
    plan_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    amount_paid: Decimal = Decimal("0")
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    status: str = "active"
    notes: Optional[str] = None


class SubscriptionCreate(BaseModel):
    """Subscription creation schema."""

    user_id: int
    plan_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    amount_paid: Decimal = Decimal("0")
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    status: str = "active"
    created_by: Optional[int] = None
    notes: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    """Subscription update schema."""

    plan_id: Optional[int] = None
    end_date: Optional[datetime] = None
    amount_paid: Optional[Decimal] = None
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class SubscriptionResponse(BaseModel):
    """Subscription response schema."""

    id: int
    user_id: int
    plan_id: Optional[int] = None
    start_date: datetime
    end_date: datetime
    amount_paid: Decimal
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_valid: bool  # 计算属性
    days_remaining: int  # 计算属性

    class Config:
        from_attributes = True


class SubscriptionLogResponse(BaseModel):
    """Subscription log response schema."""

    id: int
    subscription_id: int
    user_id: Optional[int] = None
    action: str
    old_end_date: Optional[datetime] = None
    new_end_date: Optional[datetime] = None
    details: Optional[str] = None
    performed_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionDetailResponse(SubscriptionResponse):
    """Subscription detail response with plan info."""

    plan: Optional[PlanResponse] = None
    username: Optional[str] = None  # User's username
