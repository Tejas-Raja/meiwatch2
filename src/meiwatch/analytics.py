from sqlalchemy import text
from sqlalchemy.orm import Session


def get_equipment_summary(session: Session) -> list[dict]:
    """Return equipment counts grouped by category."""

    query = text("""
        SELECT
            category,
            COUNT(*) AS equipment_count
        FROM equipment
        GROUP BY category
        ORDER BY category;
    """)

    result = session.execute(query)

    return [
        dict(row._mapping)
        for row in result
    ]

def get_sensor_statistics(session: Session) -> list[dict]:
    """Calculate statistics for every equipment sensor."""

    query = text("""
        SELECT
            e.equipment_id,
            e.name AS equipment_name,
            s.sensor_name,
            s.unit,
            COUNT(r.id) AS reading_count,
            ROUND(AVG(r.value), 2) AS average_value,
            MIN(r.value) AS minimum_value,
            MAX(r.value) AS maximum_value

        FROM equipment e

        JOIN sensor_definitions s
            ON e.id = s.equipment_id

        LEFT JOIN sensor_readings r
            ON s.id = r.sensor_id

        GROUP BY
            e.equipment_id,
            e.name,
            s.sensor_name,
            s.unit

        ORDER BY
            e.equipment_id,
            s.sensor_name;
    """)

    result = session.execute(query)

    return [
        dict(row._mapping)
        for row in result
    ]

def get_alert_summary(session: Session) -> list[dict]:
    """Summarize alerts by severity and status."""

    query = text("""
        SELECT
            severity,
            status,
            COUNT(*) AS alert_count
        FROM alerts
        GROUP BY severity, status
        ORDER BY severity, status;
    """)

    result = session.execute(query)

    return [
        dict(row._mapping)
        for row in result
    ]

def get_equipment_health_summary(session: Session) -> list[dict]:
    """Summarize readings and alerts for each equipment asset."""

    query = text("""
        WITH reading_stats AS (
            SELECT
                e.id AS equipment_id,
                COUNT(r.id) AS total_readings,

                COUNT(r.id) FILTER (
                    WHERE r.value < s.normal_min
                       OR r.value > s.normal_max
                ) AS abnormal_readings

            FROM equipment e

            LEFT JOIN sensor_definitions s
                ON e.id = s.equipment_id

            LEFT JOIN sensor_readings r
                ON s.id = r.sensor_id

            GROUP BY e.id
        ),

        alert_stats AS (
            SELECT
                e.id AS equipment_id,
                COUNT(a.id) FILTER (
                    WHERE a.status = 'open'
                ) AS open_alerts

            FROM equipment e

            LEFT JOIN sensor_definitions s
                ON e.id = s.equipment_id

            LEFT JOIN sensor_readings r
                ON s.id = r.sensor_id

            LEFT JOIN alerts a
                ON r.id = a.reading_id

            GROUP BY e.id
        )

        SELECT
            e.equipment_id,
            e.name,
            e.category,

            COALESCE(rs.total_readings, 0) AS total_readings,
            COALESCE(rs.abnormal_readings, 0) AS abnormal_readings,
            COALESCE(ast.open_alerts, 0) AS open_alerts,

            CASE
                WHEN COALESCE(rs.abnormal_readings, 0) > 0
                    THEN 'attention'
                ELSE 'normal'
            END AS monitoring_status

        FROM equipment e

        LEFT JOIN reading_stats rs
            ON e.id = rs.equipment_id

        LEFT JOIN alert_stats ast
            ON e.id = ast.equipment_id

        ORDER BY e.equipment_id;
    """)

    result = session.execute(query)

    return [
        dict(row._mapping)
        for row in result
    ]