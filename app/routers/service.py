from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List, Optional
from math import radians, cos, sin, asin, sqrt
from app.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse, ServiceSearch
from app.utils.auth import get_current_admin
from geoalchemy2 import WKTElement
from shapely.wkt import loads
from shapely.geometry import Point
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_DWithin, ST_Distance
router = APIRouter()

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r

@router.post("/", response_model=ServiceResponse)
def create_service(service: ServiceCreate, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    # Create point from lat/lng
    point = WKTElement(f'POINT({service.longitude} {service.latitude})', srid=4326)
    db_service = Service(
        name=service.name,
        category=service.category,
        location=point,
        rating=service.rating,
        created_by=current_admin.id
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    # For response, extract lat/lng
    geom = to_shape(db_service.location)
    return ServiceResponse(
        id=db_service.id,
        name=db_service.name,
        category=db_service.category,
        latitude=geom.y,
        longitude=geom.x,
        rating=db_service.rating,
        created_at=db_service.created_at
    )

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: str, service: ServiceUpdate, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if db_service.created_by != current_admin.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to update this service")
    
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    
    update_data = service.dict(exclude_unset=True)
    if 'latitude' in update_data or 'longitude' in update_data:
        lat = update_data.get('latitude', to_shape(db_service.location).y)
        lng = update_data.get('longitude', to_shape(db_service.location).x)
        point = WKTElement(f'POINT({lng} {lat})', srid=4326)
        db_service.location = point
        update_data.pop('latitude', None)
        update_data.pop('longitude', None)
    
    for key, value in update_data.items():
        setattr(db_service, key, value)
    
    db.commit()
    db.refresh(db_service)
    geom = to_shape(db_service.location)
    return ServiceResponse(
        id=db_service.id,
        name=db_service.name,
        category=db_service.category,
        latitude=geom.y,
        longitude=geom.x,
        rating=db_service.rating,
        created_at=db_service.created_at
    )

@router.delete("/{service_id}")
def delete_service(service_id: str, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    db_service = db.query(Service).filter(Service.id == service_id).first()

    if db_service.created_by != current_admin.id:
        raise HTTPException(status_code=403, detail="Not enough permissions to update this service")

    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(db_service)
    db.commit()
    return {"message": "Service deleted"}

@router.get("/", response_model=List[ServiceResponse])
def list_services(
    latitude: float = Query(...),
    longitude: float = Query(...),
    radius: float = Query(...),  # km
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    user_point = WKTElement(f"POINT({longitude} {latitude})", srid=4326)

    query = db.query(
        Service,
        ST_Distance(Service.location, user_point).label("distance")
    )

    # category filter
    if category:
        query = query.filter(Service.category == category)

    # radius filter (IMPORTANT: DB-level)
    query = query.filter(
        ST_DWithin(
            Service.location,
            user_point,
            radius * 1000  # km → meters
        )
    )

    # sort by nearest
    query = query.order_by("distance")

    # pagination
    query = query.offset((page - 1) * limit).limit(limit)

    results = query.all()

    response = []
    for svc, distance in results:
        geom = to_shape(svc.location ) # already stored as Point
        response.append(
            ServiceResponse(
                id=svc.id,
                name=svc.name,
                category=svc.category,
                latitude=geom.y,   
                longitude=geom.x, 
                rating=svc.rating,
                created_at=svc.created_at,
                distance=round(distance / 1000, 2)  # meters → km
            )
        )

    return response