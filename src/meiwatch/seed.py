from sqlalchemy import select

from meiwatch.database import SessionLocal
from meiwatch.equipment import EQUIPMENT
from meiwatch.models import EquipmentModel, SensorDefinitionModel


def seed_equipment():
    with SessionLocal() as session:
        for item in EQUIPMENT:

            # Check whether equipment already exists.
            existing = session.scalar(
                select(EquipmentModel).where(
                    EquipmentModel.equipment_id == item.equipment_id
                )
            )

            if existing:
                print(f"Skipping existing equipment: {item.equipment_id}")
                continue

            # Create equipment record.
            equipment = EquipmentModel(
                equipment_id=item.equipment_id,
                name=item.name,
                category=item.category,
                location=item.location,
            )

            # Create associated sensor definitions.
            for sensor in item.sensors:
                equipment.sensors.append(
                    SensorDefinitionModel(
                        sensor_name=sensor.name,
                        unit=sensor.unit,
                        normal_min=sensor.normal_min,
                        normal_max=sensor.normal_max,
                    )
                )

            session.add(equipment)

        session.commit()

    print("Equipment seeding completed.")


if __name__ == "__main__":
    seed_equipment()