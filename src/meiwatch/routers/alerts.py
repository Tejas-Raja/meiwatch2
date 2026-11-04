from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from meiwatch.database import get_db
from meiwatch.models import AlertModel
from meiwatch.schemas import AlertResponse, AlertStatusUpdate


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.get("/", response_model=list[AlertResponse])
def list_alerts(
    status: str | None = None,
    severity: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """List alerts with optional status and severity filters."""

    statement = select(AlertModel)

    if status is not None:
        statement = statement.where(AlertModel.status == status)

    if severity is not None:
        statement = statement.where(AlertModel.severity == severity)

    statement = (
        statement
        .order_by(AlertModel.created_at.desc(), AlertModel.id.desc())
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(statement).all()


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve one alert by ID."""

    alert = db.get(AlertModel, alert_id)

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail=f"Alert '{alert_id}' not found",
        )

    return alert


@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert_status(
    alert_id: int,
    payload: AlertStatusUpdate,
    db: Session = Depends(get_db),
):
    """Acknowledge or resolve an existing alert."""

    alert = db.get(AlertModel, alert_id)

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail=f"Alert '{alert_id}' not found",
        )

    alert.status = payload.status

    db.commit()
    db.refresh(alert)

    return alert