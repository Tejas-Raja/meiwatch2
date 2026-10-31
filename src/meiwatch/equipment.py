
from dataclasses import dataclass


@dataclass
class SensorSpec:
    name: str
    unit: str
    normal_min: float
    normal_max: float


@dataclass
class Equipment:
    equipment_id: str
    name: str
    category: str
    location: str
    sensors: list[SensorSpec]


EQUIPMENT = [
    Equipment(
        equipment_id="CNC-001",
        name="CNC Machining Center 01",
        category="machine",
        location="Production Hall A",
        sensors=[
            SensorSpec("temperature", "°C", 35, 75),
            SensorSpec("vibration", "mm/s", 0.5, 4.0),
            SensorSpec("power", "kW", 5, 25),
        ],
    ),
    Equipment(
        equipment_id="PUMP-001",
        name="Industrial Water Pump 01",
        category="machine",
        location="Utility Room A",
        sensors=[
            SensorSpec("temperature", "°C", 30, 70),
            SensorSpec("vibration", "mm/s", 0.5, 3.5),
            SensorSpec("pressure", "bar", 2, 8),
        ],
    ),
    Equipment(
        equipment_id="COMP-001",
        name="Air Compressor 01",
        category="machine",
        location="Utility Room B",
        sensors=[
            SensorSpec("temperature", "°C", 40, 90),
            SensorSpec("vibration", "mm/s", 0.5, 4.0),
            SensorSpec("pressure", "bar", 5, 10),
        ],
    ),
    Equipment(
        equipment_id="TRF-001",
        name="Distribution Transformer 01",
        category="transformer",
        location="Electrical Room A",
        sensors=[
            SensorSpec("oil_temperature", "°C", 30, 75),
            SensorSpec("winding_temperature", "°C", 35, 85),
            SensorSpec("load", "%", 20, 85),
            SensorSpec("voltage", "kV", 6.0, 6.6),
        ],
    ),
    Equipment(
        equipment_id="TRF-002",
        name="Power Transformer 02",
        category="transformer",
        location="Electrical Room B",
        sensors=[
            SensorSpec("oil_temperature", "°C", 30, 75),
            SensorSpec("winding_temperature", "°C", 35, 85),
            SensorSpec("load", "%", 20, 85),
            SensorSpec("voltage", "kV", 10.8, 11.2),
        ],
    ),
    Equipment(
        equipment_id="SWG-001",
        name="Incoming Switchgear Panel 01",
        category="switchgear",
        location="Electrical Room A",
        sensors=[
            SensorSpec("contact_temperature", "°C", 25, 65),
            SensorSpec("current", "A", 50, 400),
            SensorSpec("voltage", "kV", 6.0, 6.6),
            SensorSpec("partial_discharge", "pC", 0, 20),
        ],
    ),
    Equipment(
        equipment_id="SWG-002",
        name="Outgoing Switchgear Panel 02",
        category="switchgear",
        location="Electrical Room B",
        sensors=[
            SensorSpec("contact_temperature", "°C", 25, 65),
            SensorSpec("current", "A", 20, 250),
            SensorSpec("voltage", "kV", 10.8, 11.2),
            SensorSpec("partial_discharge", "pC", 0, 20),
        ],
    ),
]
