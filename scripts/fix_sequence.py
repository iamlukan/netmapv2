from sqlalchemy import text
from app.database import engine

def fix_sequence():
    print("Fixing floors_id_seq sequence...")
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        try:
            # Reset sequence to the next value after the max id
            # This is safer than hardcoding the sequence name
            sql = "SELECT setval(pg_get_serial_sequence('floors', 'id'), COALESCE((SELECT MAX(id)+1 FROM floors), 1), false);"
            conn.execute(text(sql))
            conn.execute(text("COMMIT"))
            print("Sequence successfully updated.")
        except Exception as e:
            print(f"Error fixing sequence: {e}")
            # Fallback for explicit name if the above fails
            try:
                print("Attempting fallback with 'floors_id_seq'...")
                conn.execute(text("ROLLBACK"))
                conn.execute(text("COMMIT"))
                conn.execute(text("SELECT setval('floors_id_seq', (SELECT MAX(id) FROM floors));"))
                conn.execute(text("COMMIT"))
                print("Fallback successful.")
            except Exception as e2:
                print(f"Fallback failed: {e2}")

if __name__ == "__main__":
    fix_sequence()
