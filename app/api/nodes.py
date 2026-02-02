from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine
from app.models.node import NetworkNode

router = APIRouter()

# Simple init of tables if they don't exist (replaces Alembic for now)
Base.metadata.create_all(bind=engine)

@router.get("/nodes")
def get_nodes(db: Session = Depends(get_db)):
    nodes = db.query(NetworkNode).all()
    
    features = [node.to_geojson() for node in nodes]
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
