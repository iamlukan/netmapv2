from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@netmap-db:5432/netmap")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    max_retries = 3
    retry_count = 0
    import time
    from sqlalchemy.exc import OperationalError

    while retry_count < max_retries:
        try:
            # Simple check to ensure connection is valid
            db.execute(text("SELECT 1"))
            yield db
            break
        except OperationalError:
            retry_count += 1
            print(f"Database connection failed. Retrying {retry_count}/{max_retries}...")
            time.sleep(1)
            if retry_count == max_retries:
                print("CRITICAL: Database unreachable after retries.")
                raise
        finally:
            if retry_count == 0 or retry_count == max_retries: # Close only if loop finished naturally
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
        # pool_pre_ping=True helps with SSH tunnel disconnects (Re-connect on stale)
        engine_ocs = create_engine(OCS_DATABASE_URL, pool_pre_ping=True)
        SessionOCS = sessionmaker(autocommit=False, autoflush=False, bind=engine_ocs)
        print(f"INFO: OCS Engine initialized with URL: {OCS_DATABASE_URL.replace(os.getenv('OCS_DB_PASS', ''), '******')}")
    except Exception as e:
        print(f"CRITICAL: Failed to initialize OCS Engine. Is the Tunnel (netmap-tunnel) running? Error: {e}")
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
