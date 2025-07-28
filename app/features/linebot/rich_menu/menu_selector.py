# app/features/linebot/rich_menu/menu_selector.py

"""
リッチメニュー選択システム

このモジュールは、ユーザーの状態に基づいて適切なリッチメニューを選択するロジックを提供します。
将来的な拡張性を考慮し、新しいメニュータイプや条件を簡単に追加できる設計になっています。

使用例:
    selector = MenuSelector()
    menu_type = selector.select_menu(user_context)
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class MenuSelector:
    """
    リッチメニューの選択ロジックを管理するクラス
    
    将来的な拡張性を考慮して、以下の機能を提供：
    - 条件ベースのメニュー選択
    - 優先順位付きの判定
    - 新しいメニュータイプの追加が容易
    """
    
    def __init__(self):
        """
        メニュー選択ルールを初期化
        
        新しいメニュータイプを追加する場合：
        1. menu_rulesに新しいルールを追加
        2. priority値を適切に設定（小さい値ほど優先度が高い）
        3. conditionsに必要な条件を定義
        """
        self.menu_rules = [
            {
                'menu_type': 'cast_unverified_menu',
                'priority': 10,  # 最高優先度：本人確認が必要なキャストを優先
                'conditions': [
                    {'field': 'user_type', 'value': 'cast'},
                    {'field': 'identity_status', 'values': ['unsubmitted', 'rejected', None]}
                ],
                'description': 'キャスト（本人確認未完了）'
            },
            {
                'menu_type': 'cast_menu',
                'priority': 20,
                'conditions': [
                    {'field': 'user_type', 'value': 'cast'},
                    {'field': 'identity_status', 'values': ['pending', 'approved']}
                ],
                'description': 'キャスト（通常）'
            },
            {
                'menu_type': 'customer_menu',
                'priority': 30,
                'conditions': [
                    {'field': 'user_type', 'value': 'customer'}
                ],
                'description': 'カスタマー'
            },
            # 将来的な拡張例：
            # {
            #     'menu_type': 'cast_vip_menu',
            #     'priority': 5,
            #     'conditions': [
            #         {'field': 'user_type', 'value': 'cast'},
            #         {'field': 'cast_rank', 'value': 'vip'},
            #         {'field': 'identity_status', 'value': 'approved'}
            #     ],
            #     'description': 'VIPキャスト専用メニュー'
            # },
            {
                'menu_type': 'default',
                'priority': 999,  # 最低優先度：どの条件にも合致しない場合のデフォルト
                'conditions': [],  # 条件なし（必ず一致）
                'description': 'デフォルトメニュー'
            }
        ]
    
    def select_menu(self, user_context: Dict[str, Any]) -> str:
        """
        ユーザーコンテキストに基づいて適切なメニューを選択
        
        Args:
            user_context: ユーザーの状態を表す辞書
                必須フィールド:
                    - user_type: str ('cast', 'customer', None)
                    - identity_status: str or None ('approved', 'pending', 'rejected', 'unsubmitted', None)
                将来的に追加可能なフィールド:
                    - subscription_status: str (有料会員ステータス)
                    - cast_rank: str (キャストランク)
                    - last_active: datetime (最終アクティブ日時)
                    - etc...
        
        Returns:
            menu_type: 選択されたメニュータイプ
        """
        logger.info(f"メニュー選択開始 - コンテキスト: {user_context}")
        
        # 優先順位順にルールをチェック
        for rule in sorted(self.menu_rules, key=lambda x: x['priority']):
            if self._check_conditions(rule['conditions'], user_context):
                logger.info(
                    f"メニュー選択完了: {rule['menu_type']} - {rule['description']} "
                    f"(優先度: {rule['priority']})"
                )
                return rule['menu_type']
        
        # ここに到達することはないはずだが、念のためデフォルトを返す
        logger.warning("どのルールにも一致しませんでした。デフォルトメニューを返します。")
        return 'default'
    
    def _check_conditions(self, conditions: List[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        """
        条件リストがすべて満たされているかチェック
        
        Args:
            conditions: チェックする条件のリスト
            context: ユーザーコンテキスト
        
        Returns:
            bool: すべての条件が満たされている場合True
        """
        for condition in conditions:
            field = condition['field']
            field_value = context.get(field)
            
            # 単一値のチェック
            if 'value' in condition:
                expected_value = condition['value']
                if field_value != expected_value:
                    logger.debug(
                        f"条件不一致: {field}={field_value} != {expected_value}"
                    )
                    return False
            
            # 複数値のチェック（いずれかに一致）
            elif 'values' in condition:
                expected_values = condition['values']
                if field_value not in expected_values:
                    logger.debug(
                        f"条件不一致: {field}={field_value} not in {expected_values}"
                    )
                    return False
            
            # 範囲チェック（将来の拡張用）
            elif 'min' in condition or 'max' in condition:
                if field_value is None:
                    return False
                if 'min' in condition and field_value < condition['min']:
                    return False
                if 'max' in condition and field_value > condition['max']:
                    return False
        
        return True
    
    def get_available_menu_types(self) -> List[str]:
        """
        利用可能なメニュータイプのリストを返す
        
        Returns:
            List[str]: メニュータイプのリスト
        """
        return [rule['menu_type'] for rule in self.menu_rules]
    
    def add_rule(self, menu_type: str, priority: int, conditions: List[Dict], description: str):
        """
        新しいメニュールールを動的に追加
        
        Args:
            menu_type: メニュータイプ
            priority: 優先度（小さいほど高優先）
            conditions: 条件リスト
            description: 説明
        """
        new_rule = {
            'menu_type': menu_type,
            'priority': priority,
            'conditions': conditions,
            'description': description
        }
        self.menu_rules.append(new_rule)
        logger.info(f"新しいメニュールールを追加: {menu_type} - {description}")