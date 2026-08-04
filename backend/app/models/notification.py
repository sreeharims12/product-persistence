import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class NotificationType(str, enum.Enum):
    PRICE_DROP = "price_drop"
    PRICE_INCREASE = "price_increase"
    RESTOCK = "restock"
    OUT_OF_STOCK = "out_of_stock"
    NEW_SELLER = "new_seller"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WEB = "web"


class NotificationStatus(str, enum.Enum):
    SENT = "sent"
    FAILED = "failed"
    PENDING = "pending"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    monitoring_request_id = Column(
        UUID(as_uuid=True), ForeignKey("monitoring_requests.id"), nullable=False, index=True
    )
    type = Column(SAEnum(NotificationType), nullable=False)
    channel = Column(SAEnum(NotificationChannel), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(SAEnum(NotificationStatus), default=NotificationStatus.PENDING)

    user = relationship("User", back_populates="notifications")
    monitoring_request = relationship("MonitoringRequest", back_populates="notifications")
