from uuid import UUID
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class MonitoringCreate(BaseModel):
    product_name: str
    interval_minutes: int = 10
    notify_email: bool = True
    notify_sms: bool = False
    notify_restock: bool = True


class MonitoringUpdate(BaseModel):
    interval_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    notify_restock: Optional[bool] = None


class MonitoringOut(BaseModel):
    id: UUID
    user_id: UUID
    product_name: str
    interval_minutes: int
    is_active: bool
    last_checked_at: Optional[datetime]
    notify_email: bool
    notify_sms: bool
    notify_restock: bool = True
    created_at: datetime
    snapshot_count: Optional[int] = 0
    latest_price: Optional[float] = None
    latest_store: Optional[str] = None
    latest_in_stock: Optional[bool] = None

    model_config = {"from_attributes": True}
