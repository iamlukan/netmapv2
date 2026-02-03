from sqlalchemy import text
from app.database import engine, Base
from app.models.floor import Floor

def migrate():
    print("Starting migration...")
    
    # 1. Ensure new tables exist (like 'floors')
    Base.metadata.create_all(bind=engine)
    print("Metadata create_all called.")

    with engine.connect() as conn:
        conn.execute(text("COMMIT")) # Ensure isolation level allows DDL
        
        # 2. Check if column exists
        try:
            conn.execute(text("SELECT floor_id FROM network_nodes LIMIT 1"))
            print("Column 'floor_id' already exists. Migration skipped.")
            return
        except Exception:
            print("Column 'floor_id' not found. Proceeding to add...")
            conn.execute(text("ROLLBACK"))

        # 3. Ensure Default Floor (ID=1) exists so existing nodes can reference it
        try:
            # Check if floor 1 exists
            res = conn.execute(text("SELECT id FROM floors WHERE id=1"))
            if not res.scalar():
                print("Creating default floor (ID=1)...")
                # Insert placeholder floor
                conn.execute(text("INSERT INTO floors (id, name, level_order, image_path, width, height) VALUES (1, 'Default Floor', 0, '', 2000, 1500)"))
                conn.execute(text("COMMIT"))
        except Exception as e:
            print(f"Error checking/creating default floor: {e}")
            conn.execute(text("ROLLBACK"))

        # 4. Add 'floor_id' column
        try:
            print("Adding 'floor_id' column to 'network_nodes'...")
            conn.execute(text("ALTER TABLE network_nodes ADD COLUMN floor_id INTEGER DEFAULT 1 NOT NULL"))
            conn.execute(text("COMMIT"))
            print("Column added.")
        except Exception as e:
            print(f"Failed to add column: {e}")
            conn.execute(text("ROLLBACK"))

        # 5. Add Foreign Key Constraint
        try:
            print("Adding Foreign Key constraint...")
            conn.execute(text("ALTER TABLE network_nodes ADD CONSTRAINT fk_nodes_floors FOREIGN KEY (floor_id) REFERENCES floors(id)"))
            conn.execute(text("COMMIT"))
            print("Constraint added.")
        except Exception as e:
            print(f"Failed to add constraint: {e}")

if __name__ == "__main__":
    migrate()
