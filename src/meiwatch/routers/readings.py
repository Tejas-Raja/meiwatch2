from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from meiwatch.database import get_db
from meiwatch.models import (
    EquipmentModel,
    SensorDefinitionModel,
    SensorReadingModel,
)
from meiwatch.schemas import SensorReadingResponse


router = APIRouter(tags=["Readings"])


@router.get("/readings", response_model=list[SensorReadingResponse])
def list_readings(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    equipment_id: str | None = None,
    db: Session = Depends(get_db),
):
    """Return sensor readings with optional equipment filtering."""

    statement = (
        select(SensorReadingModel)
        .join(SensorDefinitionModel)
        .join(EquipmentModel)
    )

    if equipment_id is not None:
        equipment_exists = db.scalar(
            select(EquipmentModel.id).where(
                EquipmentModel.equipment_id == equipment_id
            )
        )

        if equipment_exists is None:
            raise HTTPException(
                status_code=404,
                detail=f"Equipment '{equipment_id}' not found",
            )

        statement = statement.where(
            EquipmentModel.equipment_id == equipment_id
        )

    statement = (
        statement
        .order_by(
            SensorReadingModel.recorded_at.desc(),
            SensorReadingModel.id.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(statement).all()


@router.get(
    "/readings/{reading_id}",
    response_model=SensorReadingResponse,
)
def get_reading(
    reading_id: int,
    db: Session = Depends(get_db),
):
    """Return one sensor reading by its database ID."""

    reading = db.get(SensorReadingModel, reading_id)

    if reading is None:
        raise HTTPException(
            status_code=404,
            detail=f"Reading '{reading_id}' not found",
        )

    return reading


@router.get(
    "/equipment/{equipment_id}/readings",
    response_model=list[SensorReadingResponse],
)
def get_equipment_readings(
    equipment_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Return readings belonging to a specific equipment asset."""

    equipment_exists = db.scalar(
        select(EquipmentModel.id).where(
            EquipmentModel.equipment_id == equipment_id
        )
    )

    if equipment_exists is None:
        raise HTTPException(
            status_code=404,
            detail=f"Equipment '{equipment_id}' not found",
        )

    statement = (
        select(SensorReadingModel)
        .join(SensorDefinitionModel)
        .join(EquipmentModel)
        .where(EquipmentModel.equipment_id == equipment_id)
        .order_by(
            SensorReadingModel.recorded_at.desc(),
            SensorReadingModel.id.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(statement).all()