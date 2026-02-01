#!/bin/bash
set -e

echo "=== Waiting for database availability (${DB_BACK_HOST}) ==="
while ! pg_isready -h "${DB_BACK_HOST}" -p "${DB_BACK_PORT}" -U "${DB_BACK_USER}" -q; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

echo "=== PostgreSQL is ready ! ==="

echo "=== Running Alembic migrations ==="
cd /app
alembic upgrade head

echo "=== Migrations completed ! ==="

echo "=== Starting the FastAPI application ==="
exec uvicorn api.main:app --host 0.0.0.0 --port 8000

