from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_ocs_db
from app.services import ocs

from app.core.deps import get_current_user

router = APIRouter()

@router.get("/ocs/machine/{hostname}")
def get_machine_info(hostname: str, db: Session = Depends(get_ocs_db), current_user = Depends(get_current_user)):
    if db is None:
        raise HTTPException(status_code=503, detail="OCS Database not available")
    
    machine = ocs.get_machine_by_name(db, hostname)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found in OCS")
    
    return machine

@router.get("/ocs/software/search")
def search_software(q: str, db: Session = Depends(get_ocs_db), current_user = Depends(get_current_user)):
    if db is None:
        raise HTTPException(status_code=503, detail="OCS Database not available")
    
    # Return list of hostnames
    return ocs.search_machines_by_software(db, q)
