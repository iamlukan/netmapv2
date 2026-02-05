#!/bin/sh
set -e

# 1. Wait for Database
echo "Starting scripts/wait_for_db.py..."
python scripts/wait_for_db.py

# 2. Migrate & Seed
echo "Running migrations..."
python scripts/migrate_user_table.py

echo "Starting scripts/seed_admin.py..."
python scripts/seed_admin.py

# 3. Start Uvicorn
echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
