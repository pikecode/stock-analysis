"""Users API for admin management."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.user import User
from app.models.subscription import Subscription, Plan

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/admin", response_model=List[dict])
async def list_users(
    keyword: Optional[str] = Query(None, description="Search by username, email, or phone"),
    status_filter: Optional[str] = Query(None, description="Filter by user status"),
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Get all users with their subscription info (admin only)."""
    query = db.query(User)

    # Filter by keyword
    if keyword:
        query = query.filter(
            (User.username.ilike(f"%{keyword}%"))
            | (User.email.ilike(f"%{keyword}%"))
            | (User.phone.ilike(f"%{keyword}%"))
        )

    # Filter by status
    if status_filter:
        query = query.filter(User.status == status_filter)

    users = query.order_by(User.created_at.desc()).all()

    # Build response with subscription info
    result = []
    for user in users:
        # Get the most recent active subscription
        subscription = (
            db.query(Subscription)
            .filter(Subscription.user_id == user.id)
            .order_by(Subscription.end_date.desc())
            .first()
        )

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
            "status": user.status,
            "created_at": user.created_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "subscription": None,
        }

        if subscription:
            from datetime import datetime
            is_expired = datetime.utcnow() > subscription.end_date
            days_remaining = max(0, (subscription.end_date - datetime.utcnow()).days)

            plan_name = "未知套餐"
            if subscription.plan_id:
                plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
                if plan:
                    plan_name = plan.display_name

            user_data["subscription"] = {
                "id": subscription.id,
                "plan_name": plan_name,
                "start_date": subscription.start_date.isoformat(),
                "end_date": subscription.end_date.isoformat(),
                "amount_paid": str(subscription.amount_paid),
                "payment_method": subscription.payment_method,
                "status": subscription.status,
                "is_expired": is_expired,
                "days_remaining": days_remaining,
            }

        result.append(user_data)

    return result


@router.get("/admin/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Get user detail with subscription info (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Get subscription
    subscription = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id)
        .order_by(Subscription.end_date.desc())
        .first()
    )

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "status": user.status,
        "created_at": user.created_at.isoformat(),
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "subscription": None,
    }

    if subscription:
        from datetime import datetime
        is_expired = datetime.utcnow() > subscription.end_date
        days_remaining = max(0, (subscription.end_date - datetime.utcnow()).days)

        plan_name = "未知套餐"
        if subscription.plan_id:
            plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
            if plan:
                plan_name = plan.display_name

        user_data["subscription"] = {
            "id": subscription.id,
            "plan_name": plan_name,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat(),
            "amount_paid": str(subscription.amount_paid),
            "payment_method": subscription.payment_method,
            "status": subscription.status,
            "is_expired": is_expired,
            "days_remaining": days_remaining,
        }

    return user_data


@router.delete("/admin/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    _: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """Delete a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Delete related subscriptions first
    db.query(Subscription).filter(Subscription.user_id == user_id).delete()

    # Delete the user
    db.delete(user)
    db.commit()

    return None
