from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.models.monitoring import MonitoringRequest
from app.routers.auth import get_current_user
from app.schemas.product import NotificationOut

router = APIRouter()


@router.get("", response_model=List[NotificationOut])
def list_notifications(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.sent_at.desc())
        .limit(limit)
        .all()
    )
    # Enrich with product name from the monitoring request
    result = []
    for n in notifications:
        req = db.query(MonitoringRequest).filter(
            MonitoringRequest.id == n.monitoring_request_id
        ).first()
        out = NotificationOut(
            id=n.id,
            user_id=n.user_id,
            monitoring_request_id=n.monitoring_request_id,
            type=n.type.value,
            channel=n.channel.value,
            message=n.message,
            sent_at=n.sent_at,
            status=n.status.value,
            product_name=req.product_name if req else None,
        )
        result.append(out)
    return result
