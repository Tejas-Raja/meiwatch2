from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from meiwatch.database import get_db
from meiwatch.models import EquipmentModel
from meiwatch.schemas import EquipmentResponse


router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"],
)


@router.get("/", response_model=list[EquipmentResponse])
def list_equipment(
    db: Session = Depends(get_db),
):
    """Return all registered equipment."""

    statement = select(EquipmentModel).order_by(
        EquipmentModel.equipment_id
    )

    return db.scalars(statement).all()


@router.get("/{equipment_id}", response_model=EquipmentResponse)
def get_equipment(
    equipment_id: str,
    db: Session = Depends(get_db),
):
    """Return one equipment asset by its external ID."""

    statement = select(EquipmentModel).where(
        EquipmentModel.equipment_id == equipment_id
    )

    equipment = db.scalar(statement)

    if equipment is None:
        raise HTTPException(
            status_code=404,
            detail=f"Equipment '{equipment_id}' not found",
        )

    return equipment