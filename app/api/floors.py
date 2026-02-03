from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db, Base, engine
from app.models.floor import Floor
from app.models.node import NetworkNode
import shutil
import os
from PIL import Image

router = APIRouter()

# Directories
STATIC_FLOORS_DIR = os.path.join("static", "assets", "floors")
if not os.path.exists(STATIC_FLOORS_DIR):
    os.makedirs(STATIC_FLOORS_DIR)

# Init table
Base.metadata.create_all(bind=engine)

@router.get("/floors")
def get_floors(db: Session = Depends(get_db)):
    return db.query(Floor).order_by(Floor.level_order).all()

@router.post("/floors/upload")
async def upload_floor(
    file: UploadFile = File(...),
    name: str = Form(...),
    level_order: int = Form(...),
    db: Session = Depends(get_db)
):
    # Save file
    file_path = os.path.join(STATIC_FLOORS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analyze Image
    with Image.open(file_path) as img:
        width, height = img.size
    
    # Create DB Entry
    new_floor = Floor(
        name=name,
        level_order=level_order,
        image_path=f"/static/assets/floors/{file.filename}",
        width=width,
        height=height
    )
    db.add(new_floor)
    db.commit()
    db.refresh(new_floor)
    return new_floor

@router.patch("/floors/{floor_id}")
def update_floor(floor_id: int, name: str = None, level_order: int = None, db: Session = Depends(get_db)):
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    
    if name:
        floor.name = name
    if level_order is not None:
        floor.level_order = level_order
        
    db.commit()
    return floor

@router.delete("/floors/{floor_id}")
def delete_floor(floor_id: int, db: Session = Depends(get_db)):
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
        
    db.delete(floor)
    db.commit()
    return {"status": "deleted", "id": floor_id}

@router.post("/floors/{floor_id}/image")
async def update_floor_image(
    floor_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")

    # Save new file
    file_path = os.path.join(STATIC_FLOORS_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Analyze Image
    with Image.open(file_path) as img:
        width, height = img.size
    
    # Update Stats
    floor.image_path = f"/static/assets/floors/{file.filename}"
    floor.width = width
    floor.height = height
    
    db.commit()
    db.refresh(floor)
    return floor
