from sqlalchemy import Column, Integer, String, ForeignKey
from geoalchemy2 import Geometry
from app.database import Base

class NetworkNode(Base):
    __tablename__ = "network_nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Máquina, Switch, Ramal
    ip_address = Column(String, nullable=True)
    point_number = Column(String, nullable=True)
    floor_id = Column(Integer, ForeignKey('floors.id'), nullable=False, default=1)
    assigned_to = Column(String, nullable=True) # Responsible person (for Ramal/Equipamento)
    details = Column(String, nullable=True) # Extra info (Asset ID, Description, Text Content)
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)

    def to_geojson(self):
        """Helper to convert node to GeoJSON feature"""
        # Note: In a real scenario, use proper serialization libraries like shapely or geojson
        # This is a lightweight manual implementation for the MVP
        import json
        from geoalchemy2.shape import to_shape
        
        coordinates = [0, 0]
        if self.geom is not None:
             point = to_shape(self.geom)
             coordinates = [point.x, point.y]

        return {
            "type": "Feature",
            "id": self.id,
            "geometry": {
                "type": "Point",
                "coordinates": coordinates
            },
            "properties": {
                "id": self.id,
                "name": self.name,
                "type": self.type,
                "ip_address": self.ip_address,
                "point_number": self.point_number,
                "floor_id": self.floor_id,
                "floor_id": self.floor_id,
                "assigned_to": self.assigned_to,
                "details": self.details
            }
        }
