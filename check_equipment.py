from meiwatch.equipment import EQUIPMENT

print(f"Total equipment: {len(EQUIPMENT)}")

for equipment in EQUIPMENT:
    print(f"\n{equipment.equipment_id} - {equipment.name}")
    print(f"Category: {equipment.category}")
    print(f"Location: {equipment.location}")

    for sensor in equipment.sensors:
        print(
            f"  {sensor.name}: "
            f"{sensor.normal_min}-{sensor.normal_max} {sensor.unit}"
        )