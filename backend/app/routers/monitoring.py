from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.monitoring import MonitoringRequest
from app.models.product import ProductSnapshot, PriceHistory
from app.routers.auth import get_current_user
from app.schemas.monitoring import MonitoringCreate, MonitoringUpdate, MonitoringOut
from app.schemas.product import ProductSnapshotOut, PriceHistoryOut
from app.scheduler.jobs import add_monitoring_job, remove_monitoring_job

router = APIRouter()


def _enrich(req: MonitoringRequest) -> dict:
    """Add computed fields to a monitoring request."""
    data = {
        "id": req.id,
        "user_id": req.user_id,
        "product_name": req.product_name,
        "interval_minutes": req.interval_minutes,
        "is_active": req.is_active,
        "last_checked_at": req.last_checked_at,
        "notify_email": req.notify_email,
        "notify_sms": req.notify_sms,
        "notify_restock": getattr(req, "notify_restock", True),
        "created_at": req.created_at,
        "snapshot_count": len(req.snapshots) if req.snapshots else 0,
        "latest_price": None,
        "latest_store": None,
        "latest_in_stock": None,
    }
    if req.snapshots:
        latest = req.snapshots[0]  # ordered desc by captured_at
        data["latest_price"] = latest.price
        data["latest_store"] = latest.store_name
        data["latest_in_stock"] = latest.in_stock
    return data


@router.get("", response_model=List[MonitoringOut])
def list_monitoring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reqs = (
        db.query(MonitoringRequest)
        .filter(MonitoringRequest.user_id == current_user.id)
        .order_by(MonitoringRequest.created_at.desc())
        .all()
    )
    return [MonitoringOut(**_enrich(r)) for r in reqs]


@router.post("", response_model=MonitoringOut, status_code=201)
def create_monitoring(
    payload: MonitoringCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.interval_minutes not in [1, 5, 10, 30, 60]:
        raise HTTPException(status_code=400, detail="interval_minutes must be 1, 5, 10, 30, or 60")

    req = MonitoringRequest(
        user_id=current_user.id,
        product_name=payload.product_name,
        interval_minutes=payload.interval_minutes,
        is_active=True,
        notify_email=payload.notify_email,
        notify_sms=payload.notify_sms,
        notify_restock=payload.notify_restock,
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    # Schedule the job immediately
    add_monitoring_job(str(req.id), req.interval_minutes)

    return MonitoringOut(**_enrich(req))


@router.get("/{monitoring_id}", response_model=MonitoringOut)
def get_monitoring(
    monitoring_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(MonitoringRequest).filter(
        MonitoringRequest.id == monitoring_id,
        MonitoringRequest.user_id == current_user.id,
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Monitoring request not found")
    return MonitoringOut(**_enrich(req))


@router.patch("/{monitoring_id}", response_model=MonitoringOut)
def update_monitoring(
    monitoring_id: UUID,
    payload: MonitoringUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(MonitoringRequest).filter(
        MonitoringRequest.id == monitoring_id,
        MonitoringRequest.user_id == current_user.id,
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Monitoring request not found")

    if payload.interval_minutes is not None:
        if payload.interval_minutes not in [1, 5, 10, 30, 60]:
            raise HTTPException(status_code=400, detail="interval_minutes must be 1, 5, 10, 30, or 60")
        req.interval_minutes = payload.interval_minutes

    if payload.is_active is not None:
        req.is_active = payload.is_active
        if payload.is_active:
            add_monitoring_job(str(req.id), req.interval_minutes)
        else:
            remove_monitoring_job(str(req.id))

    if payload.notify_email is not None:
        req.notify_email = payload.notify_email
    if payload.notify_sms is not None:
        req.notify_sms = payload.notify_sms
    if payload.notify_restock is not None:
        req.notify_restock = payload.notify_restock

    db.commit()
    db.refresh(req)
    return MonitoringOut(**_enrich(req))


@router.delete("/{monitoring_id}", status_code=204)
def delete_monitoring(
    monitoring_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(MonitoringRequest).filter(
        MonitoringRequest.id == monitoring_id,
        MonitoringRequest.user_id == current_user.id,
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Monitoring request not found")

    remove_monitoring_job(str(req.id))
    db.delete(req)
    db.commit()


@router.get("/{monitoring_id}/snapshots", response_model=List[ProductSnapshotOut])
def get_snapshots(
    monitoring_id: UUID,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(MonitoringRequest).filter(
        MonitoringRequest.id == monitoring_id,
        MonitoringRequest.user_id == current_user.id,
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Monitoring request not found")

    snapshots = (
        db.query(ProductSnapshot)
        .filter(ProductSnapshot.monitoring_request_id == monitoring_id)
        .order_by(ProductSnapshot.captured_at.desc())
        .limit(limit)
        .all()
    )
    return snapshots


@router.get("/{monitoring_id}/price-history", response_model=List[PriceHistoryOut])
def get_price_history(
    monitoring_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(MonitoringRequest).filter(
        MonitoringRequest.id == monitoring_id,
        MonitoringRequest.user_id == current_user.id,
    ).first()
    if not req:
        raise HTTPException(status_code=404, detail="Monitoring request not found")

    history = (
        db.query(PriceHistory)
        .filter(PriceHistory.monitoring_request_id == monitoring_id)
        .order_by(PriceHistory.recorded_at.asc())
        .all()
    )
    return history
