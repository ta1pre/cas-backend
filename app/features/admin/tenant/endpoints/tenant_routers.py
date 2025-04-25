# テナント（管理アカウント）作成用ルーター雛形
from fastapi import APIRouter, Depends, HTTPException
from app.features.admin.tenant.endpoints.tenant_create import router as tenant_create_router

# 認証付きにする場合はDepends(get_current_user)などを追加

tenant_router = APIRouter(
    prefix="",
    tags=["Tenant"],
)

tenant_router.include_router(tenant_create_router, prefix="/tenant/create", tags=["Tenant - Create"])
