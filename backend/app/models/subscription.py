"""Subscription and Plan models for user access control."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Plan(Base):
    """Plan model - defines subscription plans."""

    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)

    # Pricing
    price = Column(Numeric(10, 2), nullable=False, default=0)
    original_price = Column(Numeric(10, 2))  # Original price for showing discount

    # Duration in days
    duration_days = Column(Integer, nullable=False, default=30)

    # Plan features (JSON-like, can be parsed)
    features = Column(Text)  # JSON string: ["feature1", "feature2"]

    # Status
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)  # For display ordering

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """Subscription model - tracks user subscriptions."""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id", ondelete="SET NULL"), index=True)

    # Subscription period
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False, index=True)

    # Payment info
    amount_paid = Column(Numeric(10, 2), default=0)
    payment_method = Column(String(50))  # alipay, wechat, manual, etc.
    transaction_id = Column(String(100))  # External payment ID

    # Status: active, expired, cancelled, pending
    status = Column(String(20), default="active", index=True)

    # Admin who created/modified this subscription
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Notes (for admin)
    notes = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")
    creator = relationship("User", foreign_keys=[created_by], viewonly=True)

    @property
    def is_valid(self) -> bool:
        """Check if subscription is currently valid."""
        if self.status != "active":
            return False
        return datetime.utcnow() < self.end_date

    @property
    def days_remaining(self) -> int:
        """Get remaining days of subscription."""
        if not self.is_valid:
            return 0
        delta = self.end_date - datetime.utcnow()
        return max(0, delta.days)


class SubscriptionLog(Base):
    """Log of subscription changes for audit trail."""

    __tablename__ = "subscription_logs"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Action: created, renewed, cancelled, expired, modified
    action = Column(String(50), nullable=False)

    # Details
    old_end_date = Column(DateTime)
    new_end_date = Column(DateTime)
    details = Column(Text)  # JSON for additional info

    # Who performed this action
    performed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    subscription = relationship("Subscription", backref="logs")
    performer = relationship("User", foreign_keys=[performed_by])
