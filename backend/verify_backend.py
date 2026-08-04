import time
import os
import sys

# Add current directory to python path
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add current directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from uuid import UUID
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.monitoring import MonitoringRequest
from app.models.product import ProductSnapshot, PriceHistory
from app.models.notification import Notification
from app.services.monitoring_service import run_monitoring_check
from app.routers.auth import hash_password

def verify_all():
    print("--- Verification Script ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Clean old verify user if exists
        test_email = "verify@example.com"
        old_user = db.query(User).filter(User.email == test_email).first()
        if old_user:
            db.delete(old_user)
            db.commit()

        # 2. Create User
        user = User(
            email=test_email,
            hashed_password=hash_password("password123"),
            full_name="Verification User",
            phone="+1234567890",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Created user: {user.email} (ID: {user.id})")

        # 3. Create Monitoring Request
        req = MonitoringRequest(
            user_id=user.id,
            product_name="iPhone 15",
            interval_minutes=1,
            is_active=True,
            notify_email=True,
            notify_sms=False
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        print(f"Created monitoring request for '{req.product_name}' (ID: {req.id})")

        # 4. Run first check (Initial Snapshotting)
        print("Running first check...")
        run_monitoring_check(str(req.id))

        # Check snapshots count
        snaps = db.query(ProductSnapshot).filter(ProductSnapshot.monitoring_request_id == req.id).all()
        print(f"First check done. Snapshots in database: {len(snaps)}")
        for s in snaps[:3]:
            print(f"  - {s.store_name}: ${s.price} (In Stock: {s.in_stock})")

        # 5. Run second check (simulate time delay to trigger price noise/fluctuation)
        print("Waiting 5 seconds before running second check to allow time/price simulation...")
        time.sleep(5)
        print("Running second check...")
        run_monitoring_check(str(req.id))

        # Check price history and notifications
        history = db.query(PriceHistory).filter(PriceHistory.monitoring_request_id == req.id).all()
        notifications = db.query(Notification).filter(Notification.monitoring_request_id == req.id).all()
        print(f"Second check done.")
        print(f"Total price history records: {len(history)}")
        print(f"Total notifications triggered: {len(notifications)}")
        for n in notifications:
            print(f"  - Notification: Type={n.type.value}, Status={n.status.value}, Message={n.message}")

        print("Verification completed successfully ✓")
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_all()
