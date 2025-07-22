# app/features/linebot/rich_menu/endpoints/rich_menu_routers.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from app.db.session import get_db
from app.features.linebot.services.user_info import fetch_user_info_by_line_id
from app.features.linebot.rich_menu.services.menu_manager import MenuManager
from app.features.linebot.rich_menu.services.condition_engine import MenuConditionEngine
from app.features.linebot.rich_menu.services.image_service import MenuImageService

rich_menu_router = APIRouter()

@rich_menu_router.post("/update-user-menu")
async def update_user_menu(
    line_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    指定したユーザーのRich Menuを手動更新
    """
    try:
        # ユーザー情報を取得
        user_info = fetch_user_info_by_line_id(db, line_id)
        
        # メニューを更新
        menu_manager = MenuManager()
        result = menu_manager.update_user_menu(line_id, user_info)
        
        return {
            "success": True,
            "line_id": line_id,
            "user_info": user_info,
            "menu_update_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@rich_menu_router.get("/user-menu-status")
async def get_user_menu_status(
    line_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    ユーザーのメニュー状態を確認（デバッグ用）
    """
    try:
        # ユーザー情報を取得
        user_info = fetch_user_info_by_line_id(db, line_id)
        
        # メニュー状態を取得
        menu_manager = MenuManager()
        status = menu_manager.get_user_menu_status(line_id, user_info)
        
        return {
            "success": True,
            "status": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@rich_menu_router.get("/condition-debug")
async def debug_condition_engine(
    line_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    条件判定エンジンのデバッグ情報を取得
    """
    try:
        # ユーザー情報を取得
        user_info = fetch_user_info_by_line_id(db, line_id)
        
        # 条件判定のデバッグ
        condition_engine = MenuConditionEngine()
        debug_info = condition_engine.debug_user_conditions(user_info)
        
        return {
            "success": True,
            "line_id": line_id,
            "user_info": user_info,
            "debug_info": debug_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@rich_menu_router.get("/image-status")
async def get_image_status() -> Dict[str, Any]:
    """
    利用可能な画像の状態を確認
    """
    try:
        image_service = MenuImageService()
        available_images = image_service.list_available_images()
        
        # 必要な画像のチェック
        required_images = ["unregistered", "customer_basic", "cast_basic"]
        image_status = {}
        
        for menu_type in required_images:
            image_status[menu_type] = {
                "exists": image_service.image_exists(menu_type),
                "path": image_service.get_image_path(menu_type),
                "placeholder_info": image_service.get_placeholder_info(menu_type)
            }
        
        return {
            "success": True,
            "available_images": available_images,
            "required_images_status": image_status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@rich_menu_router.post("/cleanup-menus")
async def cleanup_unused_menus(
    confirm: bool = Query(False, description="削除を確認する場合はTrue")
) -> Dict[str, Any]:
    """
    使用されていないRich Menuを削除（管理用）
    """
    try:
        if not confirm:
            return {
                "success": False,
                "message": "確認が必要です。confirm=true パラメータを追加してください。"
            }
        
        menu_manager = MenuManager()
        result = menu_manager.cleanup_unused_menus()
        
        return {
            "success": True,
            "cleanup_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@rich_menu_router.get("/health")
async def rich_menu_health_check() -> Dict[str, str]:
    """
    Rich Menu機能のヘルスチェック
    """
    return {
        "status": "ok",
        "service": "rich_menu"
    }