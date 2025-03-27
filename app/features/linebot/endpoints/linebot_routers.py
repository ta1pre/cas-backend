from fastapi import APIRouter


linebot_router = APIRouter()

# サブルーターを集約
from .webhook import router as webhook_router
linebot_router.include_router(webhook_router, prefix="/webhook", tags=["Linebot Webhook"])
