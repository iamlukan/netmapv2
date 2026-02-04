from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.node import NetworkNode

def get_inventory_discrepancies(local_db: Session, ocs_db: Session | None):
    """
    Compares Local Netmap Inventory vs OCS Remote Inventory.
    Returns:
        {
            "missing_in_ocs": [List of Nodes present in Map but not in OCS],
            "missing_in_map": [List of OCS Machines present in OCS but not in Map]
        }
    """
    
    # 1. Fetch Local Machines (Computers only)
    # We ignore 'Ponto', 'Ramal', 'Equipamento'
    local_nodes = local_db.query(NetworkNode).filter(NetworkNode.type == 'Computador').all()
    
    # Store as a set of names for O(1) lookup
    # Normalize to upper case for case-insensitive comparison
    local_names = {node.name.upper(): node for node in local_nodes}
    
    # 2. Fetch OCS Machines
    ocs_names = set()
    ocs_data = []
    
    if ocs_db:
        try:
            # Query: Name and Tag from joined tables
            # accountinfo might be named 'accountinfo' or similar, usually standard OCS is 'accountinfo'
            query = text("""
                SELECT h.NAME, a.TAG, h.MEMORY, h.PROCESSORT, b.SMODEL, h.IPADDR, h.USERID, h.OSNAME
                FROM hardware h
                LEFT JOIN accountinfo a ON h.ID = a.HARDWARE_ID
                LEFT JOIN bios b ON h.ID = b.HARDWARE_ID
                WHERE (a.TAG IS NULL OR (a.TAG NOT LIKE '%DESATIVADO%' AND a.TAG NOT LIKE '%DESATIVADA%' AND a.TAG NOT LIKE '%SERVIDORES%'))
            """)
            result = ocs_db.execute(query).fetchall()
            
            for row in result:
                # row is (NAME, TAG, MEMORY, PROCESSORT, SMODEL, IPADDR, USERID, OSNAME)
                name = str(row[0]).upper() if row[0] else ""
                
                if name:
                    ocs_names.add(name)
                    ocs_data.append({
                        "name": name, 
                        "tag": row[1],
                        "memory": row[2],
                        "processor": row[3],
                        "model": row[4],
                        "ip": row[5],
                        "user": row[6],
                        "os": row[7]
                    })
                    
        except Exception as e:
            print(f"ERROR: Failed to fetch OCS Inventory: {e}")
            # If OCS fails, we can't determine what is missing in map, 
            # but we can technically see what IS in map.
            # However, the diff would be invalid.
            return {"error": f"OCS Connection Failed: {str(e)}"}
    else:
        return {"error": "OCS Database not configured"}

    # 3. Calculate Discrepancies
    
    # A. Missing in OCS (Present in Local, but not in OCS)
    # These are computers we claim to have on the map, but OCS doesn't know about them.
    # Potential Ghost machines or incorrectly named.
    missing_in_ocs = []
    for name, node in local_names.items():
        if name not in ocs_names:
            missing_in_ocs.append({
                "id": node.id,
                "name": node.name,
                "floor_id": node.floor_id,
                # "floor_name": node.floor.name if node.floor else "Unknown" # Need relationship eager loading or joinedload if accessing children
            })
            
    # B. Missing in Map (Present in OCS, but not in Local)
    # These are real machines reporting to OCS, but we haven't placed them on the map yet.
    missing_in_map = []
    for ocs_machine in ocs_data:
        name = ocs_machine["name"]
        if name not in local_names:
            missing_in_map.append({
                "name": name,
                "tag": ocs_machine["tag"],
                "model": ocs_machine.get("model"),
                "processor": ocs_machine.get("processor"),
                "memory": ocs_machine.get("memory"),
                "ip": ocs_machine.get("ip"),
                "user": ocs_machine.get("user"),
                "os": ocs_machine.get("os")
            })
            
    # Sort for UI niceness
    missing_in_ocs.sort(key=lambda x: x["name"])
    missing_in_map.sort(key=lambda x: x["name"])
    
    return {
        "status": "success",
        "missing_in_ocs": missing_in_ocs,
        "missing_in_map": missing_in_map,
        "counts": {
            "local_computers": len(local_names),
            "ocs_machines": len(ocs_names),
            "missing_in_ocs": len(missing_in_ocs),
            "missing_in_map": len(missing_in_map)
        }
    }

from datetime import datetime, timedelta

def get_node_status_map(local_db: Session, ocs_db: Session | None):
    """
    Returns a dictionary mapping Node IDs to their status color.
    Green: Online recently (<= 3 days)
    Gray: Stale (> 3 days)
    Red: Ghost (Not in OCS)
    """
    status_map = {}
    
    # 1. Fetch Local Computers
    local_nodes = local_db.query(NetworkNode).filter(NetworkNode.type == 'Computador').all()
    
    # 2. Fetch OCS Data (Name + LastDate)
    ocs_data = {} # Name -> LastDate (datetime)
    
    if ocs_db:
        try:
            # We explicitly need LASTDATE from hardware table
            query = text("""
                SELECT h.NAME, h.LASTDATE
                FROM hardware h
                LEFT JOIN accountinfo a ON h.ID = a.HARDWARE_ID
                WHERE (a.TAG IS NULL OR (a.TAG NOT LIKE '%DESATIVADO%' AND a.TAG NOT LIKE '%DESATIVADA%' AND a.TAG NOT LIKE '%SERVIDORES%'))
            """)
            result = ocs_db.execute(query).fetchall()
            
            for row in result:
                name = str(row[0]).upper() if row[0] else ""
                last_date_raw = row[1]
                
                # Parse OCS Date (Format usually: YYYY-MM-DD HH:MM:SS or similar)
                # If it's already a datetime object (pymysql might convert), good.
                # If string, parse it.
                if isinstance(last_date_raw, str):
                    try:
                        last_date = datetime.strptime(last_date_raw, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            last_date = datetime.strptime(last_date_raw, "%Y-%m-%d")
                        except:
                            last_date = None
                elif isinstance(last_date_raw, datetime):
                    last_date = last_date_raw
                else:
                    last_date = None
                    
                if name:
                    ocs_data[name] = last_date
                    
        except Exception as e:
            print(f"ERROR: Status Map OCS Fetch failed: {e}")
            # Fallback: All Red? Or just return empty?
            # If OCS is down, everything is effectively "unknown", but "Red" implies "Missing".
            # Let's verify existing nodes against an empty set -> All Red.
            pass
            
    # 3. Determine Status
    now = datetime.now()
    cutoff_active = now - timedelta(days=3)
    
    for node in local_nodes:
        name_upper = node.name.upper()
        
        if name_upper in ocs_data:
            last_seen = ocs_data[name_upper]
            if last_seen and last_seen >= cutoff_active:
                status_map[node.id] = "green" # Active
            else:
                status_map[node.id] = "gray" # Stale
        else:
            status_map[node.id] = "red" # Missing in OCS
            
    return status_map
