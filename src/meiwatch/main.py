from fastapi import FastAPI
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
def health_check():
    return {"status": "healthy"}