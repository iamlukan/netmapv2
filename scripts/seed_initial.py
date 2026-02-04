import sys
import os

# Add parent directory to path so we can import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal
from app.models.floor import Floor

from app.models.user import User
from app.core.security import get_password_hash

def seed_initial():
    db = SessionLocal()
    try:
        # 1. Seed Floor
        count = db.query(Floor).count()
        if count > 0:
            print("INFO: Floors table not empty. Skipping floor seed.")
        else:
            print("INFO: Seeding initial floor...")
            initial_floor = Floor(
                name="Pavimento Inicial",
                level_order=1,
                image_path="/static/assets/floors/BANDRIO_1PVTO_Editado.jpg",
                width=1615,
                height=580
            )
            db.add(initial_floor)
            print("SUCCESS: Created '7º Pavimento'.")

        # 2. Seed Admin User
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("INFO: Admin user already exists. Skipping.")
        else:
            print("INFO: Creating default admin user...")
            hashed_pwd = get_password_hash("admin")
            new_admin = User(
                username="admin",
                hashed_password=hashed_pwd,
                role="admin",
                full_name="Administrator"
            )
            db.add(new_admin)
            print("SUCCESS: Created user 'admin' (password: admin).")

        db.commit()
        
    except Exception as e:
        print(f"ERROR: Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_initial()
