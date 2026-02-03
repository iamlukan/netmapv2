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

from app.core.deps import get_current_admin_user

@router.post("/nodes")
def create_node(node: NodeCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
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

from fastapi import HTTPException

@router.delete("/nodes/{node_id}")
def delete_node(node_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    node = db.query(NetworkNode).filter(NetworkNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    db.delete(node)
    db.commit()
    return {"status": "deleted", "id": node_id}

class NodeUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    point_number: str | None = None
    floor_id: int | None = None
    x: float | None = None
    y: float | None = None

@router.put("/nodes/{node_id}")
def update_node(node_id: int, node_update: NodeUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    node = db.query(NetworkNode).filter(NetworkNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    if node_update.name is not None:
        node.name = node_update.name
    if node_update.type is not None:
        node.type = node_update.type
    if node_update.point_number is not None:
        node.point_number = node_update.point_number
    if node_update.floor_id is not None:
        node.floor_id = node_update.floor_id
    
    # Update geometry if coords changed
    if node_update.x is not None and node_update.y is not None:
        node.geom = f"POINT({node_update.x} {node_update.y})"
        
    db.commit()
    return node.to_geojson()
