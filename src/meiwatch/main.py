from fastapi import FastAPI

app = FastAPI(
    title="MeiWatch2.0",
    description="Factory Operations Monitoring System",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "application": "MeiWatch2.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}