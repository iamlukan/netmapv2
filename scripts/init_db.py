import sys
import os

# Ensure the app directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
# Import all models to ensure they are registered with Base.metadata
from app.models import user, floor, node

def init_db():
    print("Creating all tables in the database...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
