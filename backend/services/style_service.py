from sqlalchemy.orm import Session
from models import SanzoWadaPalette, ClothingItem, UserOutfitLog, PaletteType, ClothingCategory
from sqlalchemy import func
import requests
import json
import random
import math
import shutil
import os
import uuid
import datetime
from fastapi import UploadFile

# Helper class for color conversion and distance
class ColorUtils:
    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hsl(r, g, b):
        r /= 255.0
        g /= 255.0
        b /= 255.0
        max_c = max(r, g, b)
        min_c = min(r, g, b)
        l = (max_c + min_c) / 2.0
        if max_c == min_c:
            h = s = 0.0
        else:
            d = max_c - min_c
            s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
            if max_c == r:
                h = (g - b) / d + (6.0 if g < b else 0.0)
            elif max_c == g:
                h = (b - r) / d + 2.0
            else:
                h = (r - g) / d + 4.0
            h /= 6.0
        return (h * 360.0, s * 100.0, l * 100.0)

    @staticmethod
    def color_distance(hex1, hex2):
        # Simple Euclidean distance in RGB space for now. 
        # Better: CIELAB Delta E.
        r1, g1, b1 = ColorUtils.hex_to_rgb(hex1)
        r2, g2, b2 = ColorUtils.hex_to_rgb(hex2)
        return math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)

class StyleService:
    def __init__(self, db: Session):
        self.db = db

    async def sync_palettes(self):
        url = "https://raw.githubusercontent.com/dblodorn/sanzo-wada/master/packages/sanzo-wada-colors/src/colors.json" 
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
            else:
                data = [
                    {"id": 1, "colors": ["#334455", "#AABBCC", "#DDEEFF"], "type": "3-color"},
                    {"id": 2, "colors": ["#112233", "#445566"], "type": "2-color"}
                ]
                print("Using fallback data for Sanzo Wada palettes.")

            count = 0
            new_palettes = []
            
            # Get existing IDs to avoid re-inserting
            existing_ids = {p.combination_id for p in self.db.query(SanzoWadaPalette.combination_id).all()}

            for item in data:
                cid = item.get('id')
                if cid not in existing_ids:
                    colors = item.get('colors', [])
                    ptype = f"{len(colors)}-color"
                    
                    palette = SanzoWadaPalette(
                        combination_id=cid,
                        combination_type=ptype,
                        colors=json.dumps(colors),
                        name=item.get('name')
                    )
                    new_palettes.append(palette)
                    count += 1
            
            if new_palettes:
                self.db.bulk_save_objects(new_palettes)
                self.db.commit()
            return count
        except Exception as e:
            print(f"Error syncing palettes: {e}")
            return 0

    async def upload_clothing_image(self, file: UploadFile):
        if not file:
            return None
        
        # Create directory if not exists
        upload_dir = "static/uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir, exist_ok=True)
            
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Return URL (Relative for now, can be made absolute in response)
        return f"/static/uploads/{unique_filename}"

    async def add_closet_item(self, user_id: int, item_data, image_file: UploadFile = None):
        image_url = item_data.image_url
        
        # If image file is provided, upload it and override url
        if image_file:
            uploaded_url = await self.upload_clothing_image(image_file)
            if uploaded_url:
                image_url = uploaded_url

        item = ClothingItem(
            user_id=user_id,
            category=item_data.category,
            sub_category=item_data.sub_category,
            primary_color_hex=item_data.primary_color_hex,
            material=item_data.material,
            image_url=image_url
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    async def get_user_closet(self, user_id: int):
        return self.db.query(ClothingItem).filter(ClothingItem.user_id == user_id).order_by(ClothingItem.created_at.desc()).all()

    async def get_daily_recommendation(self, user_id: int):
        today = datetime.date.today()
        
        # 0. Check for cached/logged outfit for today
        existing_log = self.db.query(UserOutfitLog).filter(
            UserOutfitLog.user_id == user_id, 
            UserOutfitLog.date == today
        ).first()
        
        if existing_log:
             # Reconstruct response from log
             palette = self.db.query(SanzoWadaPalette).get(existing_log.palette_id)
             item_ids = json.loads(existing_log.items)
             
             # Fetch items efficiently
             items = self.db.query(ClothingItem).filter(ClothingItem.id.in_(item_ids)).all()
             item_map = {item.id: item for item in items}
             
             outfit = {
                 "top": None, "bottom": None, "shoes": None, "outerwear": None
             }
             
             # Map back to categories (simple heuristic or store role in log)
             for item in items:
                 if item.category == ClothingCategory.TOP and not outfit["top"]: outfit["top"] = item
                 elif item.category == ClothingCategory.BOTTOM and not outfit["bottom"]: outfit["bottom"] = item
                 elif item.category == ClothingCategory.SHOES and not outfit["shoes"]: outfit["shoes"] = item
                 elif item.category == ClothingCategory.OUTERWEAR and not outfit["outerwear"]: outfit["outerwear"] = item
            
             return {
                "palette_name": palette.name if palette else "Günlük Seçim",
                "colors": json.loads(palette.colors) if palette else [],
                "outfit": outfit,
                "weather_info": "14°C, Cloudy (Cached)",
                "advice": "Bugün için seçtiğimiz kombin."
            }

        # 1. Get Weather (Mock for now)
        temp = 14 # Degrees Celsius
        weather_desc = "Cloudy"
        needs_outerwear = temp < 15
        
        # 2. Get User's Clothes
        clothes = await self.get_user_closet(user_id)
        if not clothes:
            return {"advice": "Gardırobunuz boş. Lütfen kıyafet ekleyin."}
            
        tops = [c for c in clothes if c.category == ClothingCategory.TOP]
        bottoms = [c for c in clothes if c.category == ClothingCategory.BOTTOM]
        outerwear = [c for c in clothes if c.category == ClothingCategory.OUTERWEAR]
        shoes = [c for c in clothes if c.category == ClothingCategory.SHOES]
        
        if not tops:
             return {"advice": "Kombin için en az bir üst giyim ekleyin."}

        # 3. Pick a Top (Random or logic)
        selected_top = random.choice(tops)
        
        # 4. Find matching Sanzo Wada Palette
        palettes = self.db.query(SanzoWadaPalette).all()
        best_palette = None
        min_dist = float('inf')
        
        # We need a palette that includes a color close to our top
        for p in palettes:
            p_colors = json.loads(p.colors)
            for color in p_colors:
                dist = ColorUtils.color_distance(selected_top.primary_color_hex, color)
                if dist < min_dist:
                    min_dist = dist
                    best_palette = p

        if not best_palette:
             return {"advice": "Uyumlu bir renk paleti bulunamadı."}
             
        # 5. Build Outfit from Palette
        palette_colors = json.loads(best_palette.colors)
        
        outfit = {
            "top": selected_top,
            "bottom": None,
            "shoes": None,
            "outerwear": None
        }
        
        remaining_colors = [c for c in palette_colors] # Copy
        closest_c = min(remaining_colors, key=lambda x: ColorUtils.color_distance(x, selected_top.primary_color_hex))
        if closest_c in remaining_colors:
            remaining_colors.remove(closest_c)
            
        # Helper to find best match from items for a set of target colors
        def find_match(items, target_colors):
            if not items: return None
            best_item = None
            best_item_dist = float('inf')
            matched_target = None
            
            for item in items:
                for target in target_colors:
                    dist = ColorUtils.color_distance(item.primary_color_hex, target)
                    if dist < best_item_dist:
                        best_item_dist = dist
                        best_item = item
                        matched_target = target
            return best_item, matched_target

        # Find Bottom
        best_bottom, matched_color = find_match(bottoms, remaining_colors)
        if best_bottom:
            outfit["bottom"] = best_bottom
            if matched_color in remaining_colors:
                remaining_colors.remove(matched_color)
        
        # Find Shoes
        best_shoes, matched_color = find_match(shoes, remaining_colors)
        if best_shoes:
            outfit["shoes"] = best_shoes
             if matched_color in remaining_colors:
                remaining_colors.remove(matched_color)
                
        # Find Outerwear if needed
        if needs_outerwear:
            best_outer, _ = find_match(outerwear, remaining_colors if remaining_colors else palette_colors)
            if best_outer:
                outfit["outerwear"] = best_outer

        # 6. Save Recommendation to Log
        item_ids = []
        if outfit["top"]: item_ids.append(outfit["top"].id)
        if outfit["bottom"]: item_ids.append(outfit["bottom"].id)
        if outfit["shoes"]: item_ids.append(outfit["shoes"].id)
        if outfit["outerwear"]: item_ids.append(outfit["outerwear"].id)
        
        log = UserOutfitLog(
            user_id=user_id,
            date=today,
            items=json.dumps(item_ids),
            palette_id=best_palette.id
        )
        self.db.add(log)
        self.db.commit()

        return {
            "palette_name": best_palette.name or f"Palette #{best_palette.combination_id}",
            "colors": palette_colors,
            "outfit": outfit,
            "weather_info": f"{temp}°C, {weather_desc}",
            "advice": "Bugün hava serin, dış giyim önerilir." if needs_outerwear else "Hava güzel, tadını çıkarın."
        }
