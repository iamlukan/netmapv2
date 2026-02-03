from sqlalchemy import text
from app.database import engine

def migrate():
    print("Checking 'point_number' column...")
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        try:
            conn.execute(text("SELECT point_number FROM network_nodes LIMIT 1"))
            print("Column 'point_number' already exists. Migration skipped.")
        except Exception:
            print("Column 'point_number' not found. Adding...")
            conn.execute(text("ROLLBACK"))
            try:
                conn.execute(text("ALTER TABLE network_nodes ADD COLUMN point_number VARCHAR"))
                conn.execute(text("COMMIT"))
                print("Column added successfully.")
            except Exception as e:
                print(f"Failed to add column: {e}")
                conn.execute(text("ROLLBACK"))

if __name__ == "__main__":
    migrate()
