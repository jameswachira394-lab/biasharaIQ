from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.models import User, Subscription, Payment, UserPlan, SubscriptionStatus
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    @staticmethod
    def upgrade_user(db: Session, user_id: int, plan: str, amount: float):
        """Upgrade user to a new plan."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        # Set subscription dates
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)

        # Update User
        user.plan = plan
        user.subscription_status = SubscriptionStatus.active
        user.subscription_start = start_date
        user.subscription_end = end_date
        
        # Create Subscription record
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            amount=amount,
            status=SubscriptionStatus.active,
            started_at=start_date,
            expires_at=end_date
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User {user_id} upgraded to {plan} until {end_date}")
        return user

    @staticmethod
    def check_and_update_status(db: Session, user_id: int):
        """Check if subscription has expired and downgrade if necessary."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        if user.plan == UserPlan.free:
            return user

        if user.subscription_end and user.subscription_end < datetime.utcnow():
            logger.info(f"User {user_id} subscription expired. Downgrading to FREE.")
            user.plan = UserPlan.free
            user.subscription_status = SubscriptionStatus.expired
            db.commit()
            db.refresh(user)

        return user

    @staticmethod
    def increment_transaction_count(db: Session, user_id: int):
        """Increment the monthly transaction count for the user."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.monthly_transaction_count += 1
            db.commit()
            return user.monthly_transaction_count
        return 0

    @staticmethod
    def can_add_transaction(user: User) -> bool:
        """Check if user can add more transactions."""
        if user.plan == UserPlan.pro:
            return True
        
        return user.monthly_transaction_count < 200
