"""Subscriptions API."""
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.core.database import get_db
from app.models.subscription import Subscription, SubscriptionLog, Plan
from app.models.user import User
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionUpdate,
    SubscriptionDetailResponse,
    SubscriptionLogResponse,
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get("/user/current", response_model=SubscriptionDetailResponse)
async def get_current_user_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's active subscription."""
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == current_user.id,
            Subscription.status == "active",
        )
        .order_by(Subscription.end_date.desc())
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )

    # Convert to response with plan
    response = SubscriptionDetailResponse.model_validate(subscription)
    if subscription.plan_id:
        plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
        response.plan = plan
    return response


@router.get("/user/check", response_model=dict)
async def check_subscription_validity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if user has valid subscription and remaining days."""
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == current_user.id,
            Subscription.status == "active",
        )
        .order_by(Subscription.end_date.desc())
        .first()
    )

    if not subscription:
        return {
            "is_valid": False,
            "days_remaining": 0,
            "end_date": None,
        }

    return {
        "is_valid": subscription.is_valid,
        "days_remaining": subscription.days_remaining,
        "end_date": subscription.end_date,
        "status": subscription.status,
    }


@router.get("/admin", response_model=List[SubscriptionDetailResponse])
async def list_subscriptions(
    user_id: int = None,
    status_filter: str = None,
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Get all subscriptions with optional filtering (admin only)."""
    query = db.query(Subscription)

    if user_id:
        query = query.filter(Subscription.user_id == user_id)

    if status_filter:
        query = query.filter(Subscription.status == status_filter)

    subscriptions = query.order_by(Subscription.created_at.desc()).all()

    # Convert to response with plan and user info
    result = []
    for sub in subscriptions:
        response = SubscriptionDetailResponse.model_validate(sub)

        # Add plan info if exists
        if sub.plan_id:
            plan = db.query(Plan).filter(Plan.id == sub.plan_id).first()
            response.plan = plan

        # Add user info
        user = db.query(User).filter(User.id == sub.user_id).first()
        if user:
            response.username = user.username

        result.append(response)

    return result


@router.get("/admin/{subscription_id}", response_model=SubscriptionDetailResponse)
async def get_subscription(
    subscription_id: int,
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Get subscription detail (admin only)."""
    subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    response = SubscriptionDetailResponse.model_validate(subscription)
    if subscription.plan_id:
        plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
        response.plan = plan
    return response


@router.post("/admin", response_model=SubscriptionDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionCreate,
    current_admin: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Create a subscription (admin only)."""
    # Check if user exists
    user = db.query(User).filter(User.id == subscription.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check if plan exists (if provided)
    if subscription.plan_id:
        plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found",
            )

    # Create subscription
    db_subscription = Subscription(
        user_id=subscription.user_id,
        plan_id=subscription.plan_id,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        amount_paid=subscription.amount_paid,
        payment_method=subscription.payment_method,
        transaction_id=subscription.transaction_id,
        status=subscription.status,
        created_by=current_admin.id,
        notes=subscription.notes,
    )
    db.add(db_subscription)
    db.flush()

    # Create log entry
    log = SubscriptionLog(
        subscription_id=db_subscription.id,
        user_id=subscription.user_id,
        action="created",
        new_end_date=subscription.end_date,
        details=f"Subscription created by admin",
        performed_by=current_admin.id,
    )
    db.add(log)
    db.commit()
    db.refresh(db_subscription)

    response = SubscriptionDetailResponse.model_validate(db_subscription)
    if db_subscription.plan_id:
        plan = db.query(Plan).filter(Plan.id == db_subscription.plan_id).first()
        response.plan = plan
    return response


@router.put("/admin/{subscription_id}", response_model=SubscriptionDetailResponse)
async def update_subscription(
    subscription_id: int,
    subscription: SubscriptionUpdate,
    current_admin: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Update subscription (admin only)."""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    old_end_date = db_subscription.end_date

    # Update fields
    update_data = subscription.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subscription, field, value)

    db.add(db_subscription)
    db.flush()

    # Create log entry if end_date changed
    if old_end_date != db_subscription.end_date:
        log = SubscriptionLog(
            subscription_id=db_subscription.id,
            user_id=db_subscription.user_id,
            action="modified",
            old_end_date=old_end_date,
            new_end_date=db_subscription.end_date,
            details="Subscription updated by admin",
            performed_by=current_admin.id,
        )
        db.add(log)

    db.commit()
    db.refresh(db_subscription)

    response = SubscriptionDetailResponse.model_validate(db_subscription)
    if db_subscription.plan_id:
        plan = db.query(Plan).filter(Plan.id == db_subscription.plan_id).first()
        response.plan = plan
    return response


@router.post("/admin/{subscription_id}/extend", response_model=SubscriptionDetailResponse)
async def extend_subscription(
    subscription_id: int,
    days: int,
    current_admin: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Extend subscription by days (admin only)."""
    db_subscription = db.query(Subscription).filter(Subscription.id == subscription_id).first()
    if not db_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found",
        )

    old_end_date = db_subscription.end_date
    new_end_date = db_subscription.end_date + timedelta(days=days)
    db_subscription.end_date = new_end_date
    db_subscription.status = "active"

    db.add(db_subscription)
    db.flush()

    # Create log entry
    log = SubscriptionLog(
        subscription_id=db_subscription.id,
        user_id=db_subscription.user_id,
        action="extended",
        old_end_date=old_end_date,
        new_end_date=new_end_date,
        details=f"Extended by {days} days",
        performed_by=current_admin.id,
    )
    db.add(log)
    db.commit()
    db.refresh(db_subscription)

    response = SubscriptionDetailResponse.model_validate(db_subscription)
    if db_subscription.plan_id:
        plan = db.query(Plan).filter(Plan.id == db_subscription.plan_id).first()
        response.plan = plan
    return response


@router.get("/admin/{subscription_id}/logs", response_model=List[SubscriptionLogResponse])
async def get_subscription_logs(
    subscription_id: int,
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Get subscription change logs (admin only)."""
    logs = (
        db.query(SubscriptionLog)
        .filter(SubscriptionLog.subscription_id == subscription_id)
        .order_by(SubscriptionLog.created_at.desc())
        .all()
    )
    return logs
