from uuid import UUID
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class ProductResult(BaseModel):
    """Single product result from a provider search."""
    product_name: str
    store_name: str
    price: Optional[float]
    currency: str = "USD"
    in_stock: bool
    rating: Optional[float]
    review_count: Optional[int]
    image_url: Optional[str]
    product_url: Optional[str]


class ProductSnapshotOut(BaseModel):
    id: UUID
    monitoring_request_id: UUID
    product_name: str
    store_name: str
    price: Optional[float]
    currency: str
    in_stock: bool
    rating: Optional[float]
    review_count: Optional[float]
    image_url: Optional[str]
    product_url: Optional[str]
    captured_at: datetime

    model_config = {"from_attributes": True}


class PriceHistoryOut(BaseModel):
    id: UUID
    store_name: str
    price: Optional[float]
    in_stock: bool
    recorded_at: datetime

    model_config = {"from_attributes": True}


class NotificationOut(BaseModel):
    id: UUID
    user_id: UUID
    monitoring_request_id: UUID
    type: str
    channel: str
    message: str
    sent_at: datetime
    status: str
    product_name: Optional[str] = None

    model_config = {"from_attributes": True}
