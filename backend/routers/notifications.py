from fastapi import APIRouter, Depends
from typing import List
from services.notification_service import get_pending_notifications, clear_old_notifications
from auth_utils import get_current_user
from models import User

router = APIRouter()

@router.get("/notifications", tags=["notifications"])
async def get_notifications(current_user: User = Depends(get_current_user)):
    """Kullanıcının bekleyen bildirimlerini getir"""
    notifications = get_pending_notifications(current_user.id)
    
    # Eski bildirimleri temizle
    clear_old_notifications(current_user.id)
    
    return {
        "notifications": notifications,
        "count": len(notifications)
    }
