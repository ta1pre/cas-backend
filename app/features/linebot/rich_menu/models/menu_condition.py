# app/features/linebot/rich_menu/models/menu_condition.py

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

class UserType(Enum):
    """ユーザータイプ列挙"""
    UNREGISTERED = None
    CAST = "cast"
    CUSTOMER = "customer"

class MenuType(Enum):
    """メニュータイプ列挙"""
    UNREGISTERED = "unregistered"
    CAST_BASIC = "cast_basic"
    CUSTOMER_BASIC = "customer_basic"
    # 将来拡張用
    CAST_IDENTITY_REQUIRED = "cast_identity_required"
    CAST_BANK_REQUIRED = "cast_bank_required"

@dataclass
class UserCondition:
    """ユーザーの条件情報"""
    user_type: Optional[str] = None
    setup_status: Optional[str] = None
    identity_verified: bool = False
    bank_registered: bool = False
    is_first_time: bool = False
    
    @classmethod
    def from_user_info(cls, user_info: Dict[str, Any]) -> 'UserCondition':
        """ユーザー情報辞書から条件オブジェクトを作成"""
        return cls(
            user_type=user_info.get('type'),
            setup_status=user_info.get('setup_status'),
            # 将来的に拡張
            identity_verified=False,  # TODO: 実装時に修正
            bank_registered=False,    # TODO: 実装時に修正
            is_first_time=user_info.get('id') is None
        )

@dataclass
class MenuRule:
    """メニュー選択ルール"""
    name: str
    conditions: Dict[str, Any]
    priority: int
    menu_type: MenuType
    
    def matches(self, user_condition: UserCondition) -> bool:
        """ユーザー条件がこのルールにマッチするかチェック"""
        for key, expected_value in self.conditions.items():
            actual_value = getattr(user_condition, key, None)
            if actual_value != expected_value:
                return False
        return True