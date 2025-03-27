# app/features/admin/testLogin/endpoints/test_login_routers.py
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

admin_router = APIRouter(
    tags=["Admin"],
    dependencies=[Depends(get_current_user)]
)

from app.features.admin.test_login.endpoints.test_login import router as test_login_router
admin_router.include_router(test_login_router, prefix="", tags=["Admin - test-loginルーター"])
