#!/bin/sh
set -e

# 1. Wait for Database
echo "Starting scripts/wait_for_db.py..."
python scripts/wait_for_db.py

# 2. Initialize Database (Create Tables)
echo "Initializing database schema..."
python scripts/init_db.py

# 3. Migrate & Seed
echo "Running migrations..."
# Check if migration script exists before running
if [ -f "scripts/migrate_user_table.py" ]; then
    python scripts/migrate_user_table.py
fi

echo "Starting scripts/seed_admin.py..."
python scripts/seed_admin.py

# 4. Start Uvicorn
echo "Starting Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
