from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from meiwatch.database import get_db
from meiwatch.analytics import (
    get_equipment_summary,
    get_sensor_statistics,
    get_alert_summary,
    get_equipment_health_summary,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/equipment")
def equipment_summary(
    db: Session = Depends(get_db),
):
    """Return equipment counts grouped by category."""

    return get_equipment_summary(db)


@router.get("/sensors")
def sensor_statistics(
    db: Session = Depends(get_db),
):
    """Return statistics for every sensor."""

    return get_sensor_statistics(db)


@router.get("/alerts")
def alert_summary(
    db: Session = Depends(get_db),
):
    """Return alert counts grouped by severity and status."""

    return get_alert_summary(db)


@router.get("/health")
def equipment_health(
    db: Session = Depends(get_db),
):
    """Return the monitoring status of every equipment asset."""

    return get_equipment_health_summary(db)