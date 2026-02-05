import sys
import os
sys.path.append(os.getcwd())

from app.database import get_ocs_db
from sqlalchemy import text

def debug_machine(name):
    db_gen = get_ocs_db()
    db = next(db_gen)
    
    if not db:
        print("Failed to connect to OCS DB")
    if not db:
        print("Failed to connect to OCS DB")
        return

    print("--- Checking Tables ---")
    tables = db.execute(text("SHOW TABLES")).scalars().all()
    # print(f"Tables found: {tables}") # Noise reduction
    if 'software' in tables:
        print("✓ 'software' table exists. Checking columns...")
        cols = db.execute(text("DESCRIBE software")).mappings().all()
        print("Columns in 'software':")
        for c in cols:
            print(f" - {c['Field']} ({c['Type']})")
            
    print(f"--- Debugging {name} ---")
    
    # 1. Check Hardware ID
    hw = db.execute(text("SELECT ID, NAME, WORKGROUP, IPADDR FROM hardware WHERE NAME = :name"), {"name": name}).mappings().first()
    if not hw:
        print("Machine not found in hardware table.")
        return
    
    print(f"Found Hardware: ID={hw['ID']}, NAME={hw['NAME']}, WORKGROUP={hw.get('WORKGROUP', 'N/A')}, DEFAULT_IP={hw['IPADDR']}")
    
    # 2. Check Networks Table for this ID
    nets = db.execute(text("SELECT IPADDRESS, DESCRIPTION, TYPE FROM networks WHERE HARDWARE_ID = :id"), {"id": hw['ID']}).mappings().all()
    print(f"Networks found ({len(nets)}):")
    for n in nets:
        print(f" - {n['IPADDRESS']} ({n['TYPE']})")

    # 3. Test Priority Query
    query = text("""
        SELECT 
        COALESCE(
            (SELECT IPADDRESS FROM networks WHERE HARDWARE_ID = :id AND IPADDRESS LIKE '10.20.%' LIMIT 1),
            :default_ip
        ) as CALCULATED_IP
    """)
    result = db.execute(query, {"id": hw['ID'], "default_ip": hw['IPADDR']}).scalar()
    print(f"FINAL CALCULATED IP: {result}")

def debug_software_search(term):
    db_gen = get_ocs_db()
    db = next(db_gen)
    if not db: return

    print(f"--- Searching Software: '{term}' ---")
    query = text("""
        SELECT DISTINCT h.NAME 
        FROM hardware h 
        JOIN software s ON h.ID = s.HARDWARE_ID 
        JOIN software_name n ON s.NAME_ID = n.ID
        WHERE n.NAME LIKE :software
        LIMIT 10
    """)
    results = db.execute(query, {"software": f"%{term}%"}).scalars().all()
    print(f"Found {len(results)} matches (showing max 10):")
    for r in results:
        print(f" - {r}")

if __name__ == "__main__":
    debug_machine("RJ-8640")
    debug_software_search("Google") # Test with a common term
