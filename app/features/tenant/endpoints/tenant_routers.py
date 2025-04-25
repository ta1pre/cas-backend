from fastapi import APIRouter
from app.features.tenant.endpoints import auth

tenant_router = APIRouter()

tenant_router.include_router(auth.router, prefix="/auth", tags=["Tenant Auth"])
