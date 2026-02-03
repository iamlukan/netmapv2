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

from pydantic import BaseModel

class NodeCreate(BaseModel):
    name: str
    type: str # 'Computador', 'Ponto', 'Ramal'
    ip_address: str | None = None
    point_number: str | None = None
    floor_id: int
    x: float
    y: float

@router.post("/nodes")
def create_node(node: NodeCreate, db: Session = Depends(get_db)):
    # Convert [x, y] to WKT Point
    # PostGIS standard is LON(X), LAT(Y)
    wkt = f"POINT({node.x} {node.y})"
    
    new_node = NetworkNode(
        name=node.name,
        type=node.type,
        ip_address=node.ip_address,
        point_number=node.point_number,
        floor_id=node.floor_id,
        geom=wkt
    )
    
    db.add(new_node)
    db.commit()
    db.refresh(new_node)
    return new_node.to_geojson()
