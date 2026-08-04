import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class MonitoringRequest(Base):
    __tablename__ = "monitoring_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    product_name = Column(String(500), nullable=False)
    interval_minutes = Column(Integer, default=10)  # 5, 10, 30, 60
    is_active = Column(Boolean, default=True)
    last_checked_at = Column(DateTime, nullable=True)
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    notify_restock = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="monitoring_requests")
    snapshots = relationship(
        "ProductSnapshot",
        back_populates="monitoring_request",
        cascade="all, delete-orphan",
        order_by="ProductSnapshot.captured_at.desc()",
    )
    price_history = relationship(
        "PriceHistory",
        back_populates="monitoring_request",
        cascade="all, delete-orphan",
        order_by="PriceHistory.recorded_at.asc()",
    )
    notifications = relationship(
        "Notification",
        back_populates="monitoring_request",
        cascade="all, delete-orphan",
        order_by="Notification.sent_at.desc()",
    )
