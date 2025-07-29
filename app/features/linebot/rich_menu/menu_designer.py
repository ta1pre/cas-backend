# app/features/linebot/rich_menu/menu_designer.py

"""
リッチメニュー画像生成モジュール

設定ベースでメニュー画像を生成するモジュールです。
新しいメニュータイプは menu_config.py に設定を追加することで対応できます。
"""

from PIL import Image, ImageDraw, ImageFont
import os
from typing import Tuple, List, Dict, Any
import requests
from io import BytesIO
from .menu_config import (
    get_menu_config, 
    get_button_colors,
    MENU_CONFIGURATIONS
)

class MenuDesigner:
    def __init__(self):
        self.width = 2500
        self.height = 1686
        self.grid_cols = 3
        self.grid_rows = 2
        
    def create_menu_image(self, menu_type: str) -> Image:
        """
        メニュータイプに応じた画像を生成
        
        Args:
            menu_type: メニュータイプ（cast_menu, cast_unverified_menu, customer_menu, default）
        
        Returns:
            Image: 生成されたメニュー画像
        """
        # ベース画像を作成
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img)
        
        # 設定からメニューを生成
        config = get_menu_config(menu_type)
        return self._create_menu_from_config(img, draw, menu_type, config)
    
    def _create_menu_from_config(self, img: Image, draw: ImageDraw.Draw, menu_type: str, config: Dict[str, Any]) -> Image:
        """
        設定に基づいてメニューを生成
        
        Args:
            img: ベース画像
            draw: 描画オブジェクト
            menu_type: メニュータイプ
            config: メニュー設定
        
        Returns:
            Image: 生成されたメニュー画像
        """
        # アイテムリストを作成
        items = []
        colors = get_button_colors(menu_type)
        
        for idx, area in enumerate(config['areas']):
            item = {
                "text": area['text'],
                "color": colors[idx] if idx < len(colors) else "#999999"
            }
            items.append(item)
        
        # グリッド設定を取得
        grid = config.get('grid', {'cols': 3, 'rows': 2})
        background_color = config.get('background_color', '#FFFFFF')
        
        # グリッドサイズに応じて描画メソッドを選択
        if grid['cols'] == 2 and grid['rows'] == 2:
            self._draw_2x2_menu(img, draw, items, base_color=background_color)
        else:
            # デフォルトは3x2グリッド
            self.grid_cols = grid['cols']
            self.grid_rows = grid['rows']
            self._draw_grid_menu(img, draw, items, base_color=background_color)
        
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
                    font_large = ImageFont.truetype(font_path, 60)  # テキスト用のフォントサイズを大きく
                    font_small = ImageFont.truetype(font_path, 60)  # 同じサイズに統一
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
        
        # テキストのみを中央に配置（アイコンは削除）
        text_bbox = draw.textbbox((0, 0), item["text"], font=font_large)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x + (width - text_width) // 2
        text_y = y + (height - text_height) // 2
        draw.text((text_x, text_y), item["text"], fill="white", font=font_large)
    
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
                    font_large = ImageFont.truetype(font_path, 80)  # テキスト用のフォントサイズを調整
                    font_small = ImageFont.truetype(font_path, 80)  # 同じサイズに統一
                    break
                except:
                    continue
                    
            if not font_large:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
                
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # マルチラインテキストのみを中央に配置（アイコンは削除）
        lines = item["text"].split("\n")
        line_height = 90  # 行間を広くする
        total_height = len(lines) * line_height
        start_y = y + (height - total_height) // 2
        
        for i, line in enumerate(lines):
            text_bbox = draw.textbbox((0, 0), line, font=font_large)
            text_width = text_bbox[2] - text_bbox[0]
            text_x = x + (width - text_width) // 2
            text_y = start_y + i * line_height
            draw.text((text_x, text_y), line, fill="white", font=font_large)
    
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
        
        # 設定に登録されているすべてのメニュータイプの画像を生成
        for menu_type in MENU_CONFIGURATIONS.keys():
            img = self.create_menu_image(menu_type)
            img.save(f"{output_dir}/{menu_type}.png")
            print(f"画像保存: {output_dir}/{menu_type}.png")


if __name__ == "__main__":
    designer = MenuDesigner()
    designer.save_menu_images()