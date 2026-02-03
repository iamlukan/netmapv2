from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, get_ocs_db
from app.services import inventory

router = APIRouter()

@router.get("/inventory/audit")
def audit_inventory(
    local_db: Session = Depends(get_db),
    ocs_db: Session = Depends(get_ocs_db)
):
    """
    Returns an audit report comparing Netmap computers vs OCS Inventory.
    Use this to identify:
    - Machines on the map that don't exist in OCS (Ghost/Typos).
    - Machines in OCS that haven't been mapped yet.
    """
    
    # If OCS is missing (None), the service handles it gracefully by returning an error dict.
    # We pass it through.
    
    result = inventory.get_inventory_discrepancies(local_db, ocs_db)
    
    if "error" in result:
        # We return 200 even on logical error to allow UI to display the error message nicely?
        # Or 503? Let's return 200 with the error field as per function signature
        return result
        
    return result

@router.get("/inventory/status")
def get_inventory_status(
    local_db: Session = Depends(get_db),
    ocs_db: Session = Depends(get_ocs_db)
):
    """
    Returns a simple map of NodeID -> Status Color (green, gray, red).
    """
    return inventory.get_node_status_map(local_db, ocs_db)
