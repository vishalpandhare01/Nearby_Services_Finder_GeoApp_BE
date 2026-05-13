import uuid
from sqlalchemy import Column, ForeignKey, String, Float, TIMESTAMP, func, Index
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.base import Base

class Service(Base):
    __tablename__ = "services"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # hospital, ATM, shop, etc.
    location = Column(
        Geometry(geometry_type="POINT", srid=4326),
        nullable=False
    )
    rating = Column(Float, nullable=True)
    created_by = Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )


# index for faster category filtering
Index("idx_services_category", Service.category)
