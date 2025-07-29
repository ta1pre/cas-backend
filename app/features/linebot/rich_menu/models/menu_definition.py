# app/features/linebot/rich_menu/models/menu_definition.py

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class MenuArea:
    """メニューのタップ可能エリア"""
    x: int
    y: int
    width: int
    height: int
    action_type: str = "uri"
    uri: str = "https://google.com"
    label: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """LINE API用の辞書形式に変換"""
        action_dict = {
            "type": self.action_type,
            "uri": self.uri
        }
        
        # labelが設定されている場合のみ追加
        if self.label:
            action_dict["label"] = self.label
            
        return {
            "bounds": {
                "x": self.x,
                "y": self.y,
                "width": self.width,
                "height": self.height
            },
            "action": action_dict
        }

@dataclass
class MenuSize:
    """メニューサイズ"""
    width: int = 2500
    height: int = 1686
    
    def to_dict(self) -> Dict[str, int]:
        """辞書形式に変換"""
        return {"width": self.width, "height": self.height}

@dataclass
class RichMenuDefinition:
    """Rich Menuの定義"""
    name: str
    areas: List[MenuArea]
    image_path: str
    size: MenuSize = None
    selected: bool = False
    
    def __post_init__(self):
        if self.size is None:
            self.size = MenuSize()
    
    def to_create_payload(self) -> Dict[str, Any]:
        """LINE API Rich Menu作成用のペイロードに変換"""
        return {
            "size": self.size.to_dict(),
            "selected": self.selected,
            "name": self.name,
            "chatBarText": self.name,
            "areas": [area.to_dict() for area in self.areas]
        }