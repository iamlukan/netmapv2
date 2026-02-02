from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, get_ocs_db

router = APIRouter()

@router.get("/test-db")
def test_db_connections(
    local_db: Session = Depends(get_db),
    ocs_db: Session = Depends(get_ocs_db)
):
    """
    Diagnose database connections.
    Returns status for 'local' and 'ocs'.
    """
    status = {
        "local": "UNKNOWN",
        "ocs": "UNKNOWN"
    }

    # Check Local DB
    try:
        local_db.execute(text("SELECT 1"))
        status["local"] = "OK"
    except Exception as e:
        status["local"] = f"ERROR: {str(e)}"

    # Check OCS DB
    if ocs_db is None:
        status["ocs"] = "DESATIVADO (Engine não inicializada ou URL não configurada)"
    else:
        try:
            ocs_db.execute(text("SELECT 1"))
            status["ocs"] = "OK"
        except Exception as e:
            status["ocs"] = f"ERROR: {str(e)}"

    return status
