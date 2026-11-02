from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    DateTime,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from meiwatch.database import Base

from datetime import datetime

class EquipmentModel(Base):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    equipment_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)

    sensors: Mapped[list["SensorDefinitionModel"]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
    )


class SensorDefinitionModel(Base):
    __tablename__ = "sensor_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
    )
    sensor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    normal_min: Mapped[float] = mapped_column(Float, nullable=False)
    normal_max: Mapped[float] = mapped_column(Float, nullable=False)

    equipment: Mapped["EquipmentModel"] = relationship(
        back_populates="sensors"
    )

    __table_args__ = (
        UniqueConstraint(
            "equipment_id",
            "sensor_name",
            name="uq_sensor_equipment_name",
        ),
        CheckConstraint(
            "normal_min < normal_max",
            name="ck_sensor_valid_range",
        ),
    )

class SensorReadingModel(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    sensor_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_definitions.id", ondelete="CASCADE"),
        nullable=False,
    )

    value: Mapped[float] = mapped_column(Float, nullable=False)

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    sensor: Mapped["SensorDefinitionModel"] = relationship()

    alert: Mapped["AlertModel | None"] = relationship(
        back_populates="reading",
        uselist=False,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_readings_sensor_recorded", "sensor_id", "recorded_at"),
    )

class AlertModel(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    reading_id: Mapped[int] = mapped_column(
        ForeignKey("sensor_readings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(String(20), nullable=False)

    message: Mapped[str] = mapped_column(String(255), nullable=False)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    reading: Mapped["SensorReadingModel"] = relationship(
        back_populates="alert"
    )

    __table_args__ = (
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name="ck_alert_valid_severity",
        ),
        CheckConstraint(
            "status IN ('open', 'acknowledged', 'resolved')",
            name="ck_alert_valid_status",
        ),
        Index("ix_alerts_status_created", "status", "created_at"),
    )