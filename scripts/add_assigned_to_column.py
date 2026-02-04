from sqlalchemy import text, inspect
import sys
import os

# Add parent dir to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import engine

def migrate():
    print("INFO: Checking database schema...")
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns('network_nodes')]
    
    if 'assigned_to' in columns:
        print("INFO: Column 'assigned_to' already exists.")
        return

    print("INFO: Column 'assigned_to' missing. Attempting migration...")
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE network_nodes ADD COLUMN assigned_to VARCHAR;"))
            conn.commit()
        print("SUCCESS: Added column 'assigned_to'.")
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")

if __name__ == "__main__":
    migrate()
