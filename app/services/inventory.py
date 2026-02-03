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
                SELECT h.NAME, a.TAG
                FROM hardware h
                LEFT JOIN accountinfo a ON h.ID = a.HARDWARE_ID
                WHERE (a.TAG IS NULL OR (a.TAG NOT LIKE '%DESATIVADO%' AND a.TAG NOT LIKE '%DESATIVADA%'))
            """)
            result = ocs_db.execute(query).fetchall()
            
            for row in result:
                # row is (NAME, TAG)
                name = str(row[0]).upper() if row[0] else ""
                
                if name:
                    ocs_names.add(name)
                    ocs_data.append({"name": name, "tag": row[1]})
                    
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
                "tag": ocs_machine["tag"]
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
