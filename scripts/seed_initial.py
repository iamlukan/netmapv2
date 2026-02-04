import sys
import os

# Add parent directory to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models.floor import Floor

def seed_initial():
    db = SessionLocal()
    try:
        # Check if floors exist
        count = db.query(Floor).count()
        if count > 0:
            print("INFO: Floors table not empty. Skipping seed.")
            return

        print("INFO: Seeding initial floor...")
        # Check if default image exists (it should, as per validation earlier)
        # Note: The path in DB must match the URL path expected by Frontend
        
        initial_floor = Floor(
            name="7º Pavimento",
            level_order=7,
            image_path="/static/assets/floors/BANDRIO_1PVTO_Editado.jpg",
            width=1615, # Using dimensions from earlier database check
            height=580
        )
        
        db.add(initial_floor)
        db.commit()
        print("SUCCESS: Created '7º Pavimento'.")
        
    except Exception as e:
        print(f"ERROR: Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_initial()
