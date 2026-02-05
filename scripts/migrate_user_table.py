import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import engine

def migrate_users_table():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS force_password_change BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("Migration successful: Added force_password_change column to users table.")
        except Exception as e:
            print(f"Migration failed (it might already exist): {e}")

if __name__ == "__main__":
    migrate_users_table()
