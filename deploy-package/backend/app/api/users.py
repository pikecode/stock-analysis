"""Users API for admin management."""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.subscription import Subscription, Plan
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


class SubscriptionInput(BaseModel):
    """Input model for subscription when creating/updating users."""
    plan_id: Optional[int] = None  # Optional: admin can set dates directly without a plan
    start_date: datetime
    end_date: datetime
    amount_paid: float = 0
    payment_method: Optional[str] = None


class CreateUserRequest(BaseModel):
    """Input model for creating a user."""
    username: str
    password: str
    role: str  # "admin", "vip", "normal"
    subscription: Optional[SubscriptionInput] = None  # Only for VIP users


class UpdateUserRequest(BaseModel):
    """Input model for updating a user."""
    password: Optional[str] = None  # Only update if provided
    role: Optional[str] = None  # "admin", "vip", "normal"
    subscription: Optional[SubscriptionInput] = None  # For updating subscription dates and payment info


@router.get("/admin", response_model=List[dict])
async def list_users(
    keyword: Optional[str] = Query(None, description="Search by username, email, or phone"),
    status_filter: Optional[str] = Query(None, description="Filter by user status"),
    _: User = Depends(require_role("admin")),
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
            "role": user.role.value,
            "status": user.status,
            "created_at": user.created_at.isoformat(),
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "subscription": None,
        }

        if subscription:
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
    _: User = Depends(require_role("admin")),
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
        "role": user.role.value,
        "status": user.status,
        "created_at": user.created_at.isoformat(),
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "subscription": None,
    }

    if subscription:
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


@router.post("/admin", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Create a new user (admin only)."""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Validate role (convert to uppercase to handle case-insensitive input)
    try:
        role = UserRole(request.role.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}",
        )

    # Create new user
    user = User(
        username=request.username,
        password_hash=get_password_hash(request.password),
        email=f"{request.username}@temp.com",  # Temporary email
        role=role,
        status="active",
    )

    db.add(user)
    db.flush()  # Flush to get the user ID

    # Create subscription if provided and role is VIP
    if request.subscription:
        if role != UserRole.VIP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subscription can only be added for VIP users",
            )

        subscription = Subscription(
            user_id=user.id,
            plan_id=request.subscription.plan_id,
            start_date=request.subscription.start_date,
            end_date=request.subscription.end_date,
            amount_paid=request.subscription.amount_paid,
            payment_method=request.subscription.payment_method,
            status="active",
        )
        db.add(subscription)

    db.commit()

    # Return user data
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.value,
        "message": "User created successfully",
    }


@router.put("/admin/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    request: UpdateUserRequest,
    _: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Update a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update password if provided
    if request.password:
        user.password_hash = get_password_hash(request.password)

    # Update role if provided (convert to uppercase to handle case-insensitive input)
    if request.role is not None:
        try:
            user.role = UserRole(request.role.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}",
            )

    # Update subscription if provided
    if request.subscription is not None:
        subscription = (
            db.query(Subscription)
            .filter(Subscription.user_id == user_id)
            .order_by(Subscription.end_date.desc())
            .first()
        )

        if subscription:
            # Update existing subscription
            subscription.plan_id = request.subscription.plan_id
            subscription.start_date = request.subscription.start_date
            subscription.end_date = request.subscription.end_date
            subscription.amount_paid = request.subscription.amount_paid
            subscription.payment_method = request.subscription.payment_method
        else:
            # Create new subscription if doesn't exist
            subscription = Subscription(
                user_id=user_id,
                plan_id=request.subscription.plan_id,
                start_date=request.subscription.start_date,
                end_date=request.subscription.end_date,
                amount_paid=request.subscription.amount_paid,
                payment_method=request.subscription.payment_method,
                status="active",
            )
            db.add(subscription)

    db.commit()

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.value,
        "message": "User updated successfully",
    }


@router.delete("/admin/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    _: User = Depends(require_role("admin")),
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
