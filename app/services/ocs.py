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
    # We join with 'bios' to get the Model (SMODEL)
    # We prioritize IP from 'networks' table where IP starts with 10.20.
    query = text("""
        SELECT h.ID, h.NAME, h.WORKGROUP, h.OSNAME, h.LASTDATE, h.USERID, h.MEMORY, h.PROCESSORT as PROCESSOR, b.SMODEL as MODEL,
        (SELECT SUM(DISKSIZE) FROM storages WHERE HARDWARE_ID = h.ID) as DISKSIZE,
        COALESCE(
            (SELECT IPADDRESS FROM networks WHERE HARDWARE_ID = h.ID AND IPADDRESS LIKE '10.20.%' LIMIT 1),
            h.IPADDR
        ) as IPADDR
        FROM hardware h
        LEFT JOIN bios b ON h.ID = b.HARDWARE_ID
        WHERE h.NAME = :name
        LIMIT 1
    """)
    
    try:
        result = db.execute(query, {"name": name}).mappings().first()
        if result:
            data = dict(result)
            # Fetch Top 5 Softwares for Compliance/Check
            # Avoiding common noise if possible, but for now just taking 5 diverse ones
            # OCS software table is normalized (ID references)
            soft_query = text("""
                SELECT n.NAME, v.VERSION 
                FROM software s
                JOIN software_name n ON s.NAME_ID = n.ID
                LEFT JOIN software_version v ON s.VERSION_ID = v.ID
                WHERE s.HARDWARE_ID = :id 
                AND n.NAME NOT LIKE 'Update for %'
                AND n.NAME NOT LIKE 'Security Update %'
                AND n.NAME NOT LIKE 'Hotfix %'
                ORDER BY n.NAME ASC 
                LIMIT 5
            """)
            softwares = db.execute(soft_query, {"id": data['ID']}).mappings().all()
            data['softwares'] = [dict(s) for s in softwares]
            return data
        return None
    except Exception as e:
        print(f"Error querying OCS: {e}")
        return None

def search_machines_by_software(db: Session, software_name: str) -> list[str]:
    """
    Find all machine names that have a software matching the query.
    """
    if db is None:
        return []

    query = text("""
        SELECT DISTINCT h.NAME 
        FROM hardware h 
        JOIN software s ON h.ID = s.HARDWARE_ID 
        JOIN software_name n ON s.NAME_ID = n.ID
        WHERE n.NAME LIKE :software
    """)
    
    try:
        # We use wildcards for partial match
        search_term = f"%{software_name}%"
        result = db.execute(query, {"software": search_term}).scalars().all()
        return list(result)
    except Exception as e:
        print(f"Error searching software: {e}")
        return []
