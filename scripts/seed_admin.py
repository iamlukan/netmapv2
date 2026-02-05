import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.core.security import get_password_hash

# Init DB
Base.metadata.create_all(bind=engine)

def create_admin_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("Creating admin user...")
            password = os.getenv("ADMIN_PASSWORD", "admin123")
            hashed_pw = get_password_hash(password)
            admin = User(
                username="admin",
                full_name="Administrator",
                hashed_password=hashed_pw,
                role="admin"
            )
            db.add(admin)
            db.commit()
            print(f"Admin user created: admin / {password}")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error seeding admin: {e}")
        # Dont crash, just log errors
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
