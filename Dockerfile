
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and database migrations
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini .

EXPOSE 8000

# Apply migrations, seed initial equipment, then start the API
CMD ["sh", "-c", "alembic upgrade head && python -m meiwatch.seed && uvicorn meiwatch.main:app --host 0.0.0.0 --port 8000"]