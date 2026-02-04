import sys
import os
from sqlalchemy import text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def migrate():
    with engine.connect() as conn:
        try:
            print("Attempting to add 'assigned_to' column to network_nodes...")
            # Postgres syntax
            conn.execute(text("ALTER TABLE network_nodes ADD COLUMN assigned_to VARCHAR(255)"))
            conn.commit()
            print("Migration successful.")
        except Exception as e:
            print(f"Migration failed (Column might already exist): {e}")

if __name__ == "__main__":
    migrate()
