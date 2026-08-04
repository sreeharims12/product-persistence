"""
monitoring_service.py
Core job that runs for each monitoring request:
  1. Fetch new product data via providers
  2. Compare with the latest snapshot
  3. Persist new snapshots + price history
  4. Detect changes and dispatch notifications
  5. Update monitoring_request.last_checked_at
"""
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.monitoring import MonitoringRequest
from app.models.product import ProductSnapshot, PriceHistory
from app.models.notification import Notification, NotificationType, NotificationChannel, NotificationStatus
from app.services.product_search import search_products
from app.services.change_detection import detect_changes
from app.services.notification_service import dispatch_notification

logger = logging.getLogger(__name__)

CHANGE_TYPE_MAP = {
    "price_drop":     NotificationType.PRICE_DROP,
    "price_increase": NotificationType.PRICE_INCREASE,
    "restock":        NotificationType.RESTOCK,
    "out_of_stock":   NotificationType.OUT_OF_STOCK,
    "new_seller":     NotificationType.NEW_SELLER,
}


def run_monitoring_check(monitoring_id: str) -> None:
    """
    Main scheduled job entry point.
    Creates its own DB session so it is safe to run from a background thread.
    """
    db: Session = SessionLocal()
    try:
        _execute_check(db, monitoring_id)
    except Exception as e:
        logger.error(f"[Monitor] Error checking {monitoring_id}: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def _execute_check(db: Session, monitoring_id: str) -> None:
    # Load monitoring request
    req: Optional[MonitoringRequest] = db.query(MonitoringRequest).filter(
        MonitoringRequest.id == UUID(monitoring_id),
        MonitoringRequest.is_active == True,
    ).first()

    if not req:
        logger.warning(f"[Monitor] Request {monitoring_id} not found or inactive — skipping")
        return

    logger.info(f"[Monitor] Checking '{req.product_name}' (id={monitoring_id})")

    # ── Step 1: Fetch fresh data ─────────────────────────────────────────────
    new_results = search_products(req.product_name)
    if not new_results:
        logger.warning(f"[Monitor] No results for '{req.product_name}'")
        return

    # ── Step 2: Load latest snapshots (one per store) ───────────────────────
    from sqlalchemy import func
    subq = (
        db.query(
            ProductSnapshot.store_name,
            func.max(ProductSnapshot.captured_at).label("max_captured")
        )
        .filter(ProductSnapshot.monitoring_request_id == req.id)
        .group_by(ProductSnapshot.store_name)
        .subquery()
    )
    old_snapshots: List[ProductSnapshot] = (
        db.query(ProductSnapshot)
        .join(subq, (ProductSnapshot.store_name == subq.c.store_name) &
                    (ProductSnapshot.captured_at == subq.c.max_captured))
        .filter(ProductSnapshot.monitoring_request_id == req.id)
        .all()
    )

    # ── Step 3: Detect changes ───────────────────────────────────────────────
    new_as_dicts = [
        {
            "product_name": r.product_name,
            "store_name":   r.store_name,
            "price":        r.price,
            "in_stock":     r.in_stock,
        }
        for r in new_results
    ]
    changes = detect_changes(old_snapshots, new_as_dicts)

    # ── Step 4: Persist snapshots & price history ────────────────────────────
    for result in new_results:
        snapshot = ProductSnapshot(
            monitoring_request_id=req.id,
            product_name=result.product_name,
            store_name=result.store_name,
            price=result.price,
            currency=result.currency,
            in_stock=result.in_stock,
            rating=result.rating,
            review_count=result.review_count,
            image_url=result.image_url,
            product_url=result.product_url,
            raw_data={
                "product_name": result.product_name,
                "store_name":   result.store_name,
                "price":        result.price,
                "in_stock":     result.in_stock,
                "rating":       result.rating,
            },
            captured_at=datetime.utcnow(),
        )
        db.add(snapshot)

        history = PriceHistory(
            monitoring_request_id=req.id,
            store_name=result.store_name,
            price=result.price,
            in_stock=result.in_stock,
            recorded_at=datetime.utcnow(),
        )
        db.add(history)

    # ── Step 5: Send notifications for detected changes ──────────────────────
    user = req.user
    for change in changes:
        change_type = CHANGE_TYPE_MAP.get(change["type"])
        if not change_type:
            continue

        subject = f"[Product Monitor] {req.product_name} — {change['type'].replace('_', ' ').title()}"
        message = change.get("message", "A change was detected for your monitored product.")

        channels = [("web", NotificationChannel.WEB)]
        if req.notify_email and user.email:
            channels.append(("email", NotificationChannel.EMAIL))
        if req.notify_sms and user.phone:
            channels.append(("sms", NotificationChannel.SMS))

        for ch_str, ch_enum in channels:
            ok = dispatch_notification(
                channel=ch_str,
                email=user.email,
                phone=user.phone,
                subject=subject,
                message=f"{req.product_name}\n\n{message}",
            )
            notif = Notification(
                user_id=user.id,
                monitoring_request_id=req.id,
                type=change_type,
                channel=ch_enum,
                message=message,
                sent_at=datetime.utcnow(),
                status=NotificationStatus.SENT if ok else NotificationStatus.FAILED,
            )
            db.add(notif)
            logger.info(f"[Monitor] Notification ({ch_str}): {change['type']} for {req.product_name}")

    # ── Step 6: Update last_checked_at ──────────────────────────────────────
    req.last_checked_at = datetime.utcnow()
    db.commit()

    logger.info(
        f"[Monitor] Done — '{req.product_name}': "
        f"{len(new_results)} results, {len(changes)} changes detected"
    )
