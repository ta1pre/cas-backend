# app/features/linebot/rich_menu/menu_designer.py

from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, List
import requests
from io import BytesIO

class MenuDesigner:
    def __init__(self):
        self.width = 2500
        self.height = 1686
        self.grid_cols = 3
        self.grid_rows = 2
        
    def create_menu_image(self, menu_type: str) -> Image:
        """メニュータイプに応じた画像を生成"""
        # ベース画像を作成
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)
        
        # メニュー設定を取得
        if menu_type == "cast_menu":
            return self._create_cast_menu(img, draw)
        elif menu_type == "customer_menu":
            return self._create_customer_menu(img, draw)
        else:
            return self._create_default_menu(img, draw)
    
    def _create_cast_menu(self, img: Image, draw: ImageDraw.Draw) -> Image:
        """キャストメニューのデザイン"""
        items = [
            {"icon": "🏠", "text": "HOME", "color": "#FF6B6B"},
            {"icon": "📅", "text": "RESERVE", "color": "#4ECDC4"},
            {"icon": "💰", "text": "SALES", "color": "#45B7D1"},
            {"icon": "👤", "text": "PROFILE", "color": "#96CEB4"},
            {"icon": "💬", "text": "MESSAGE", "color": "#FECA57"},
            {"icon": "⚙️", "text": "SETTINGS", "color": "#DDA0DD"}
        ]
        
        self._draw_grid_menu(img, draw, items, base_color="#FFE5E5")
        return img
    
    def _create_customer_menu(self, img: Image, draw: ImageDraw.Draw) -> Image:
        """カスタマーメニューのデザイン"""
        items = [
            {"icon": "🏠", "text": "HOME", "color": "#6C5CE7"},
            {"icon": "🔍", "text": "SEARCH", "color": "#A29BFE"},
            {"icon": "❤️", "text": "FAVORITE", "color": "#FD79A8"},
            {"icon": "📅", "text": "HISTORY", "color": "#74B9FF"},
            {"icon": "👤", "text": "PROFILE", "color": "#81ECEC"},
            {"icon": "💳", "text": "PAYMENT", "color": "#FDCB6E"}
        ]
        
        self._draw_grid_menu(img, draw, items, base_color="#E5E5FF")
        return img
    
    def _create_default_menu(self, img: Image, draw: ImageDraw.Draw) -> Image:
        """デフォルトメニューのデザイン（未登録ユーザー用）"""
        # 4つの大きなボタン
        items = [
            {"icon": "🚀", "text": "LOGIN\nNOW", "color": "#00B894"},
            {"icon": "❓", "text": "HOW TO\nUSE", "color": "#00CEC9"},
            {"icon": "📱", "text": "ABOUT\nAPP", "color": "#6C5CE7"},
            {"icon": "📋", "text": "TERMS\nOF USE", "color": "#636E72"}
        ]
        
        # 2x2のグリッドで描画
        self._draw_2x2_menu(img, draw, items, base_color="#E5FFF5")
        return img
    
    def _draw_grid_menu(self, img: Image, draw: ImageDraw.Draw, items: List[dict], base_color: str):
        """3x2グリッドでメニューを描画"""
        cell_width = self.width // self.grid_cols
        cell_height = self.height // self.grid_rows
        
        # 背景色
        draw.rectangle([0, 0, self.width, self.height], fill=base_color)
        
        for idx, item in enumerate(items):
            col = idx % self.grid_cols
            row = idx // self.grid_cols
            
            x = col * cell_width
            y = row * cell_height
            
            # セルを描画
            self._draw_cell(draw, x, y, cell_width, cell_height, item)
    
    def _draw_2x2_menu(self, img: Image, draw: ImageDraw.Draw, items: List[dict], base_color: str):
        """2x2グリッドでメニューを描画"""
        cell_width = self.width // 2
        cell_height = self.height // 2
        
        # 背景色
        draw.rectangle([0, 0, self.width, self.height], fill=base_color)
        
        for idx, item in enumerate(items[:4]):
            col = idx % 2
            row = idx // 2
            
            x = col * cell_width
            y = row * cell_height
            
            # より大きなセルを描画
            self._draw_large_cell(draw, x, y, cell_width, cell_height, item)
    
    def _draw_cell(self, draw: ImageDraw.Draw, x: int, y: int, width: int, height: int, item: dict):
        """個別のセルを描画"""
        # 枠線
        border_color = "#E0E0E0"
        draw.rectangle([x, y, x + width - 1, y + height - 1], outline=border_color, width=2)
        
        # 内側の丸角矩形
        margin = 20
        radius = 20
        self._draw_rounded_rectangle(
            draw, 
            x + margin, 
            y + margin, 
            x + width - margin, 
            y + height - margin,
            radius,
            fill=item["color"]
        )
        
        # アイコンとテキスト用フォント
        try:
            # 日本語対応フォントを試行
            font_paths = [
                "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc", 
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/System/Library/Fonts/PingFang.ttc"
            ]
            
            font_large = None
            font_small = None
            
            for font_path in font_paths:
                try:
                    font_large = ImageFont.truetype(font_path, 80)
                    font_small = ImageFont.truetype(font_path, 35)
                    break
                except:
                    continue
                    
            if not font_large:
                # フォントが見つからない場合はデフォルト
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
                
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # アイコン（絵文字）
        icon_bbox = draw.textbbox((0, 0), item["icon"], font=font_large)
        icon_width = icon_bbox[2] - icon_bbox[0]
        icon_height = icon_bbox[3] - icon_bbox[1]
        icon_x = x + (width - icon_width) // 2
        icon_y = y + height // 2 - icon_height - 20
        draw.text((icon_x, icon_y), item["icon"], fill="white", font=font_large)
        
        # テキスト
        text_bbox = draw.textbbox((0, 0), item["text"], font=font_small)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = x + (width - text_width) // 2
        text_y = y + height // 2 + 20
        draw.text((text_x, text_y), item["text"], fill="white", font=font_small)
    
    def _draw_large_cell(self, draw: ImageDraw.Draw, x: int, y: int, width: int, height: int, item: dict):
        """大きなセルを描画（デフォルトメニュー用）"""
        # 枠線
        border_color = "#E0E0E0"
        draw.rectangle([x, y, x + width - 1, y + height - 1], outline=border_color, width=3)
        
        # 内側の丸角矩形
        margin = 40
        radius = 30
        self._draw_rounded_rectangle(
            draw, 
            x + margin, 
            y + margin, 
            x + width - margin, 
            y + height - margin,
            radius,
            fill=item["color"]
        )
        
        # アイコンとテキスト用フォント
        try:
            # 日本語対応フォントを試行
            font_paths = [
                "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc", 
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/System/Library/Fonts/PingFang.ttc"
            ]
            
            font_large = None
            font_small = None
            
            for font_path in font_paths:
                try:
                    font_large = ImageFont.truetype(font_path, 120)
                    font_small = ImageFont.truetype(font_path, 45)
                    break
                except:
                    continue
                    
            if not font_large:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
                
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # アイコン
        icon_bbox = draw.textbbox((0, 0), item["icon"], font=font_large)
        icon_width = icon_bbox[2] - icon_bbox[0]
        icon_height = icon_bbox[3] - icon_bbox[1]
        icon_x = x + (width - icon_width) // 2
        icon_y = y + height // 2 - icon_height - 40
        draw.text((icon_x, icon_y), item["icon"], fill="white", font=font_large)
        
        # マルチラインテキスト
        lines = item["text"].split("\n")
        line_height = 60
        total_height = len(lines) * line_height
        start_y = y + height // 2 + 40
        
        for i, line in enumerate(lines):
            text_bbox = draw.textbbox((0, 0), line, font=font_small)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = x + (width - text_width) // 2
            text_y = start_y + i * line_height
            draw.text((text_x, text_y), line, fill="white", font=font_small)
    
    def _draw_rounded_rectangle(self, draw, x1, y1, x2, y2, radius, fill):
        """角丸矩形を描画"""
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill)
        draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill)
    
    def save_menu_images(self):
        """全てのメニュー画像を保存"""
        output_dir = "/tmp/rich_menu_images"
        os.makedirs(output_dir, exist_ok=True)
        
        for menu_type in ["cast_menu", "customer_menu", "default"]:
            img = self.create_menu_image(menu_type)
            img.save(f"{output_dir}/{menu_type}.png")
            print(f"画像保存: {output_dir}/{menu_type}.png")


if __name__ == "__main__":
    designer = MenuDesigner()
    designer.save_menu_images()