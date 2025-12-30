from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from services.style_service import StyleService
from services.auth import get_current_user
from models import User
from pydantic import BaseModel
from typing import List, Optional
import enum

router = APIRouter(
    prefix="/style",
    tags=["Style Engine"],
    responses={404: {"description": "Not found"}},
)

class ClothingCategory(str, enum.Enum):
    TOP = "Top"
    BOTTOM = "Bottom"
    OUTERWEAR = "Outerwear"
    SHOES = "Shoes"
    ACCESSORY = "Accessory"

class ClothingItemCreate(BaseModel):
    category: ClothingCategory
    sub_category: str
    primary_color_hex: str
    material: Optional[str] = None
    image_url: Optional[str] = None

class PaletteSyncResponse(BaseModel):
    message: str
    count: int

class RecommendationResponse(BaseModel):
    palette_name: Optional[str]
    colors: List[str]
    outfit: dict
    weather_info: str
    advice: str

@router.post("/sync-palettes", response_model=PaletteSyncResponse)
async def sync_palettes(db: Session = Depends(get_db)):
    """GitHub'dan Sanzo Wada paletlerini çeker ve veritabanına kaydeder."""
    service = StyleService(db)
    count = await service.sync_palettes()
    return {"message": "Paletler başarıyla senkronize edildi.", "count": count}

@router.post("/closet/add-item")
async def add_closet_item(
    item: ClothingItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcının dolabına kıyafet ekler."""
    service = StyleService(db)
    new_item = await service.add_closet_item(current_user.id, item)
    return new_item

@router.get("/closet")
async def get_closet(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Kullanıcının dolabındaki kıyafetleri listeler."""
    service = StyleService(db)
    return await service.get_user_closet(current_user.id)

@router.get("/daily-recommendation", response_model=RecommendationResponse)
async def get_daily_recommendation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Hava durumu ve Sanzo Wada teorisine göre kombin önerisi sunar."""
    service = StyleService(db)
    return await service.get_daily_recommendation(current_user.id)

