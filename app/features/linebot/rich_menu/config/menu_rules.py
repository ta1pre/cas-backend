# app/features/linebot/rich_menu/config/menu_rules.py

from app.features.linebot.rich_menu.models.menu_condition import MenuRule, MenuType

# Phase 1: 基本の3パターン
MENU_RULES = [
    # Cast基本メニュー
    MenuRule(
        name="cast_basic",
        conditions={
            "user_type": "cast"
        },
        priority=1,
        menu_type=MenuType.CAST_BASIC
    ),
    
    # Customer基本メニュー
    MenuRule(
        name="customer_basic", 
        conditions={
            "user_type": "customer"
        },
        priority=2,
        menu_type=MenuType.CUSTOMER_BASIC
    ),
    
    # 未登録ユーザーメニュー（デフォルト）
    MenuRule(
        name="unregistered",
        conditions={
            "user_type": None
        },
        priority=99,  # 最低優先度（フォールバック）
        menu_type=MenuType.UNREGISTERED
    )
]

# Phase 2以降で追加予定のルール（コメントアウト）
# FUTURE_RULES = [
#     MenuRule(
#         name="cast_identity_required",
#         conditions={
#             "user_type": "cast",
#             "identity_verified": False
#         },
#         priority=0,  # 最高優先度
#         menu_type=MenuType.CAST_IDENTITY_REQUIRED
#     ),
#     MenuRule(
#         name="cast_bank_required",
#         conditions={
#             "user_type": "cast", 
#             "identity_verified": True,
#             "bank_registered": False
#         },
#         priority=1,
#         menu_type=MenuType.CAST_BANK_REQUIRED
#     )
# ]