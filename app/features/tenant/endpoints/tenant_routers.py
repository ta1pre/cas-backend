from fastapi import APIRouter
from app.features.tenant.endpoints import auth
from app.features.tenant.cast.endpoints import cast

tenant_router = APIRouter()

tenant_router.include_router(auth.router, prefix="/auth", tags=["Tenant Auth"])
tenant_router.include_router(cast.router, prefix="/cast", tags=["Tenant Cast"])
