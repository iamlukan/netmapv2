from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

def get_machine_by_name(db: Session, name: str) -> Optional[dict]:
    """
    Query OCS 'hardware' table for machine details.
    """
    if db is None:
        return None

    # OCS table 'hardware' usually contains: ID, NAME, WORKGROUP, OSNAME, IPADDR, LASTDATE/LASTCOME
    query = text("""
        SELECT NAME, OSNAME, IPADDR, LASTDATE, USERID, MEMORY
        FROM hardware
        WHERE NAME = :name
        LIMIT 1
    """)
    
    try:
        result = db.execute(query, {"name": name}).mappings().first()
        if result:
            return dict(result)
        return None
    except Exception as e:
        print(f"Error querying OCS: {e}")
        return None
