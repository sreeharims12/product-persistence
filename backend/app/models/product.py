import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class ProductSnapshot(Base):
    __tablename__ = "product_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitoring_request_id = Column(
        UUID(as_uuid=True), ForeignKey("monitoring_requests.id"), nullable=False, index=True
    )
    product_name = Column(String(500), nullable=False)
    store_name = Column(String(200), nullable=False)
    price = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    in_stock = Column(Boolean, default=True)
    rating = Column(Float, nullable=True)
    review_count = Column(Float, nullable=True)
    image_url = Column(String(1000), nullable=True)
    product_url = Column(String(1000), nullable=True)
    raw_data = Column(JSONB, nullable=True)
    captured_at = Column(DateTime, default=datetime.utcnow, index=True)

    monitoring_request = relationship("MonitoringRequest", back_populates="snapshots")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    monitoring_request_id = Column(
        UUID(as_uuid=True), ForeignKey("monitoring_requests.id"), nullable=False, index=True
    )
    store_name = Column(String(200), nullable=False)
    price = Column(Float, nullable=True)
    in_stock = Column(Boolean, default=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    monitoring_request = relationship("MonitoringRequest", back_populates="price_history")
