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
            hashed_pw = get_password_hash("admin123")
            admin = User(
                username="admin",
                full_name="Administrator",
                hashed_password=hashed_pw,
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("Admin user created: admin / admin123")
        else:
            print("Admin user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
