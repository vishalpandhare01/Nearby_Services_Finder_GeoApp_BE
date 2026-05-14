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


@router.post("/", response_model=ServiceResponse)
def create_service(service: ServiceCreate, db: Session = Depends(get_db), current_admin = Depends(get_current_admin)):
    # Create point from lat/lng
    point = WKTElement(f'POINT({service.longitude} {service.latitude})', srid=4326)
    db_service = Service(
        name=service.name,
        category=service.category.lower(),
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

@router.get("/my-services", response_model=List[ServiceResponse])
def get_my_services(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    services = (
        db.query(Service)
        .filter(Service.created_by == current_admin.id)
        .all()
    )

    response = []

    for svc in services:
        geom = to_shape(svc.location)

        response.append(
            ServiceResponse(
                id=svc.id,
                name=svc.name,
                category=svc.category,
                latitude=geom.y,
                longitude=geom.x,
                rating=svc.rating,
                created_at=svc.created_at,
                distance=0  # optional if required in schema
            )
        )

    return response

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
    user_point = func.ST_SetSRID(
    func.ST_MakePoint(longitude, latitude),
    4326
)

    query = db.query(
        Service,
        ST_Distance(
            func.Geography(Service.location),
            func.Geography(user_point)
        ).label("distance")
    )

    if category:
        query = query.filter(func.lower(Service.category) == category.lower())

    query = query.filter(
        ST_DWithin(
            func.Geography(Service.location),
            func.Geography(user_point),
            radius * 1000
        )
    )

    query = query.order_by("distance")

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
