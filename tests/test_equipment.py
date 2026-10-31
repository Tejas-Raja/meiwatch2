
from meiwatch.equipment import EQUIPMENT


def test_equipment_count():
    assert len(EQUIPMENT) == 7


def test_equipment_ids_are_unique():
    equipment_ids = [
        equipment.equipment_id
        for equipment in EQUIPMENT
    ]

    assert len(equipment_ids) == len(set(equipment_ids))


def test_all_equipment_have_sensors():
    for equipment in EQUIPMENT:
        assert len(equipment.sensors) > 0


def test_sensor_ranges_are_valid():
    for equipment in EQUIPMENT:
        for sensor in equipment.sensors:
            assert sensor.normal_min < sensor.normal_max
            assert sensor.unit
            assert sensor.name
