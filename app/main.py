from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.service import router as service_router
from app.database import engine
from app.config import settings
import asyncio

app = FastAPI()

# CORS
allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Middleware
from app.middleware.auth import AuthMiddleware
app.add_middleware(AuthMiddleware)

# Routers
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(service_router, prefix="/api/v1/service", tags=["service"])
