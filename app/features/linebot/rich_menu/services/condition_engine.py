# app/features/linebot/rich_menu/services/condition_engine.py

from typing import Dict, Any, Optional
from app.features.linebot.rich_menu.models.menu_condition import UserCondition, MenuType
from app.features.linebot.rich_menu.config.menu_rules import MENU_RULES

class MenuConditionEngine:
    """ユーザー条件に基づいてメニューを決定するエンジン"""
    
    def __init__(self):
        self.rules = sorted(MENU_RULES, key=lambda x: x.priority)
    
    def evaluate_user_conditions(self, user_info: Dict[str, Any]) -> UserCondition:
        """ユーザー情報から条件オブジェクトを作成"""
        return UserCondition.from_user_info(user_info)
    
    def select_menu_type(self, user_condition: UserCondition) -> MenuType:
        """ユーザー条件に基づいて最適なメニュータイプを選択"""
        
        # 優先度順にルールをチェック
        for rule in self.rules:
            if rule.matches(user_condition):
                return rule.menu_type
        
        # フォールバック（通常発生しない）
        return MenuType.UNREGISTERED
    
    def get_menu_type_for_user(self, user_info: Dict[str, Any]) -> MenuType:
        """ユーザー情報から直接メニュータイプを取得（便利メソッド）"""
        user_condition = self.evaluate_user_conditions(user_info)
        return self.select_menu_type(user_condition)
    
    def debug_user_conditions(self, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """デバッグ用：ユーザー条件と選択されたメニューを返す"""
        user_condition = self.evaluate_user_conditions(user_info)
        selected_menu = self.select_menu_type(user_condition)
        
        return {
            "user_condition": user_condition.__dict__,
            "selected_menu": selected_menu.value,
            "applied_rules": [
                {
                    "rule_name": rule.name,
                    "matches": rule.matches(user_condition),
                    "priority": rule.priority
                }
                for rule in self.rules
            ]
        }