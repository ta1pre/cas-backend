from fastapi import APIRouter
from .referral_code import router as referral_code_router

referral_router = APIRouter()

# /get_code エンドポイントを含める
referral_router.include_router(referral_code_router, prefix="", tags=["Referral"])
