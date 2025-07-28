# app/features/linebot/rich_menu/menu_config.py

"""
リッチメニュー設定管理モジュール

このモジュールは、各メニュータイプの設定を一元管理します。
将来的にはデータベースやYAMLファイルから設定を読み込むことも可能です。

メニュー追加方法:
1. MENU_CONFIGURATIONSに新しいメニュータイプを追加
2. PAGE_ROUTING_MAPにページルーティング情報を追加
3. menu_designer.pyでデザインを実装
"""

from typing import Dict, List, Any

# メニュー設定
# 新しいメニューを追加する場合は、このディクショナリに設定を追加
MENU_CONFIGURATIONS: Dict[str, Dict[str, Any]] = {
    # キャストメニュー（通常）
    'cast_menu': {
        'name': 'キャストメニュー',
        'chat_bar_text': 'キャストメニュー',
        'areas': [
            {'action': 'home', 'icon': '🏠', 'text': 'ホーム', 'position': 0},
            {'action': 'reserve', 'icon': '📅', 'text': '予約管理', 'position': 1},
            {'action': 'sales', 'icon': '💰', 'text': '売上', 'position': 2},
            {'action': 'profile', 'icon': '👤', 'text': 'プロフィール', 'position': 3},
            {'action': 'message', 'icon': '📝', 'text': 'ポスト', 'position': 4},
            {'action': 'settings', 'icon': '⚙️', 'text': '設定', 'position': 5}
        ],
        'background_color': '#FFE5E5',  # 薄いピンク
        'grid': {'cols': 3, 'rows': 2}
    },
    
    # キャストメニュー（本人確認必要）
    'cast_unverified_menu': {
        'name': 'キャストメニュー（本人確認必要）',
        'chat_bar_text': 'キャストメニュー',
        'areas': [
            {'action': 'home', 'icon': '🏠', 'text': 'ホーム', 'position': 0},
            {'action': 'reserve', 'icon': '📅', 'text': '予約管理', 'position': 1},
            {'action': 'identity', 'icon': '⚠️', 'text': '本人確認', 'position': 2},  # 売上の位置に本人確認
            {'action': 'profile', 'icon': '👤', 'text': 'プロフィール', 'position': 3},
            {'action': 'message', 'icon': '📝', 'text': 'ポスト', 'position': 4},
            {'action': 'settings', 'icon': '⚙️', 'text': '設定', 'position': 5}
        ],
        'background_color': '#FFE5E5',  # 薄いピンク
        'grid': {'cols': 3, 'rows': 2}
    },
    
    # カスタマーメニュー
    'customer_menu': {
        'name': 'カスタマーメニュー',
        'chat_bar_text': 'カスタマーメニュー',
        'areas': [
            {'action': 'home', 'icon': '🏠', 'text': 'ホーム', 'position': 0},
            {'action': 'search', 'icon': '🔍', 'text': '検索', 'position': 1},
            {'action': 'favorite', 'icon': '❤️', 'text': 'お気に入り', 'position': 2},
            {'action': 'history', 'icon': '📅', 'text': '履歴', 'position': 3},
            {'action': 'profile', 'icon': '👤', 'text': 'プロフィール', 'position': 4},
            {'action': 'payment', 'icon': '💳', 'text': '支払い', 'position': 5}
        ],
        'background_color': '#E5E5FF',  # 薄い紫
        'grid': {'cols': 3, 'rows': 2}
    },
    
    # デフォルトメニュー（未登録ユーザー）
    'default': {
        'name': 'デフォルトメニュー',
        'chat_bar_text': 'メニュー',
        'areas': [
            {'action': 'login', 'icon': '🚀', 'text': '今すぐ\nログイン', 'position': 0},
            {'action': 'help', 'icon': '❓', 'text': '使い方', 'position': 1},
            {'action': 'about', 'icon': '📱', 'text': 'アプリ\nについて', 'position': 2},
            {'action': 'terms', 'icon': '📋', 'text': '利用規約', 'position': 3}
        ],
        'background_color': '#E5FFF5',  # 薄い緑
        'grid': {'cols': 2, 'rows': 2}  # 2x2のグリッド
    }
}

# ページルーティングマップ
# actionからURLへのマッピング
PAGE_ROUTING_MAP: Dict[str, Dict[str, str]] = {
    'cast': {
        'home': '/p/cast/cont/dashboard',
        'reserve': '/p/cast/reserve',
        'sales': '/p/cast/earnings',
        'profile': '/p/cast/profile',
        'message': '/p/cast/cont/posts',  # ポスト（ミニログ）
        'settings': '/p/cast/settings',
        'identity': '/p/cast/cont/identity_verification'  # 本人確認ページ
    },
    'customer': {
        'home': '/p/customer/dashboard',
        'search': '/p/customer/search',
        'favorite': '/p/customer/favorites',
        'history': '/p/customer/history',
        'profile': '/p/customer/profile',
        'payment': '/p/customer/payments'
    },
    'default': {
        'login': '/auth/login',
        'help': '/help',
        'about': '/about',
        'terms': '/terms'
    }
}

# ボタンカラー設定
# 各メニュータイプごとのボタンカラー
BUTTON_COLORS: Dict[str, List[str]] = {
    'cast_menu': [
        '#FF6B6B',  # 赤
        '#4ECDC4',  # ターコイズ
        '#45B7D1',  # 青
        '#96CEB4',  # 緑
        '#FECA57',  # 黄
        '#DDA0DD'   # 紫
    ],
    'cast_unverified_menu': [
        '#FF6B6B',  # 赤
        '#4ECDC4',  # ターコイズ
        '#FFA500',  # オレンジ（本人確認を目立たせる）
        '#96CEB4',  # 緑
        '#FECA57',  # 黄
        '#DDA0DD'   # 紫
    ],
    'customer_menu': [
        '#6C5CE7',  # 紫
        '#A29BFE',  # 薄紫
        '#FD79A8',  # ピンク
        '#74B9FF',  # 青
        '#81ECEC',  # 水色
        '#FDCB6E'   # オレンジ
    ],
    'default': [
        '#00B894',  # 緑
        '#00CEC9',  # ターコイズ
        '#6C5CE7',  # 紫
        '#636E72'   # グレー
    ]
}

def get_menu_config(menu_type: str) -> Dict[str, Any]:
    """
    指定されたメニュータイプの設定を取得
    
    Args:
        menu_type: メニュータイプ
    
    Returns:
        Dict: メニュー設定。存在しない場合はデフォルト設定を返す
    """
    return MENU_CONFIGURATIONS.get(menu_type, MENU_CONFIGURATIONS['default'])

def get_routing_map(user_type: str) -> Dict[str, str]:
    """
    ユーザータイプに応じたルーティングマップを取得
    
    Args:
        user_type: ユーザータイプ（cast, customer, default）
    
    Returns:
        Dict: ルーティングマップ
    """
    # cast_unverified_menuもcastのルーティングを使用
    if user_type.startswith('cast'):
        return PAGE_ROUTING_MAP['cast']
    return PAGE_ROUTING_MAP.get(user_type, PAGE_ROUTING_MAP['default'])

def get_button_colors(menu_type: str) -> List[str]:
    """
    メニュータイプに応じたボタンカラーを取得
    
    Args:
        menu_type: メニュータイプ
    
    Returns:
        List[str]: カラーコードのリスト
    """
    return BUTTON_COLORS.get(menu_type, BUTTON_COLORS['default'])