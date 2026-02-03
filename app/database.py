from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@netmap-db:5432/netmap")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# OCS Database Connection (Optional/Resilient)
# OCS Database Connection (Resilient)
OCS_DB_HOST = os.getenv("OCS_DB_HOST")
OCS_DATABASE_URL = os.getenv("OCS_DATABASE_URL")

# If Host/User/Pass/Name defined, build URL. Else fall back to full URL string.
if OCS_DB_HOST:
    _user = os.getenv("OCS_DB_USER", "ocs")
    _pass = os.getenv("OCS_DB_PASS", "ocs")
    _name = os.getenv("OCS_DB_NAME", "ocsweb")
    _port = os.getenv("OCS_DB_PORT", "3306") # Default MySQL Port
    
    OCS_DATABASE_URL = f"mysql+pymysql://{_user}:{_pass}@{OCS_DB_HOST}:{_port}/{_name}"

engine_ocs = None
SessionOCS = None

if OCS_DATABASE_URL:
    try:
        engine_ocs = create_engine(OCS_DATABASE_URL, pool_pre_ping=True)
        SessionOCS = sessionmaker(autocommit=False, autoflush=False, bind=engine_ocs)
    except Exception as e:
        print(f"WARNING: Failed to initialize OCS Engine: {e}")
        engine_ocs = None
else:
    print("WARNING: OCS_DATABASE_URL not set. OCS features will be disabled.")

def get_ocs_db():
    """
    Dependency that yields an OCS session or None if unavailable.
    Consumers must check if db is None.
    """
    if SessionOCS is None:
        yield None
        return

    db = SessionOCS()
    try:
        yield db
    finally:
        db.close()
