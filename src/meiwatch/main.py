from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from meiwatch.database import get_db
from meiwatch.routers import equipment, readings, alerts, analytics

app = FastAPI(
    title="MeiWatch2.0",
    description="Factory Operations Monitoring System",
    version="1.0.0",
)

app.include_router(equipment.router)
app.include_router(readings.router)
app.include_router(alerts.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {
        "application": "MeiWatch2.0",
        "status": "running",
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected"
            }
        )