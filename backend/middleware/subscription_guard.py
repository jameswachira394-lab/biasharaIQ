from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import User, UserPlan
from middleware.auth import get_current_user
from services.subscription_service import SubscriptionService

def require_pro(current_user: User = Depends(get_current_user)):
    """Dependency to require a PRO plan."""
    if current_user.plan != UserPlan.pro:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature requires a PRO subscription"
        )
    return current_user

def check_transaction_limit(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Dependency to check if user can add more transactions."""
    # Ensure status is up to date
    user = SubscriptionService.check_and_update_status(db, current_user.id)
    
    if not SubscriptionService.can_add_transaction(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Monthly transaction limit reached (200). Upgrade to PRO for unlimited tracking."
        )
    return user
