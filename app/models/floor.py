from sqlalchemy import Column, Integer, String
from app.database import Base

class Floor(Base):
    __tablename__ = "floors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    level_order = Column(Integer, default=0, index=True)
    image_path = Column(String, nullable=False)  # Relative path like /static/assets/floors/file.jpg
    width = Column(Integer, default=2000)
    height = Column(Integer, default=1500)
