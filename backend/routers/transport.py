from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import json

from database import get_db
from models import TransportRoute, UserTransportAlarm, User
from auth_utils import get_current_user
from services.transport_service import (
    calculate_next_bus,
    get_user_alarms_with_next_buses,
    should_trigger_alarm
)

router = APIRouter()

# Pydantic modeller
class TransportRouteResponse(BaseModel):
    id: int
    route_number: str
    route_name: str
    departure_location: str
    arrival_location: str
    departure_times: List[str]
    active_days: List[int]
    
    class Config:
        from_attributes = True

class AlarmCreate(BaseModel):
    route_id: int
    travel_time_to_stop: int  # dakika
    notification_minutes_before: int = 0

class AlarmUpdate(BaseModel):
    travel_time_to_stop: Optional[int] = None
    notification_minutes_before: Optional[int] = None
    alarm_enabled: Optional[bool] = None

class AlarmResponse(BaseModel):
    id: int
    route_id: int
    travel_time_to_stop: int
    alarm_enabled: bool
    notification_minutes_before: int
    
    class Config:
        from_attributes = True

@router.get("/transport/routes", tags=["transport"])
async def get_routes(
    departure: Optional[str] = None,
    arrival: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Tüm otobüs hatlarını listele"""
    query = db.query(TransportRoute)
    
    if departure:
        query = query.filter(TransportRoute.departure_location.ilike(f"%{departure}%"))
    if arrival:
        query = query.filter(TransportRoute.arrival_location.ilike(f"%{arrival}%"))
    
    routes = query.all()
    
    result = []
    for route in routes:
        try:
            departure_times = json.loads(route.departure_times)
            active_days = json.loads(route.active_days)
        except:
            departure_times = []
            active_days = [0, 1, 2, 3, 4, 5, 6]
        
        result.append({
            "id": route.id,
            "route_number": route.route_number,
            "route_name": route.route_name,
            "departure_location": route.departure_location,
            "arrival_location": route.arrival_location,
            "departure_times": departure_times,
            "active_days": active_days
        })
    
    return result

@router.get("/transport/routes/{route_id}", tags=["transport"])
async def get_route(route_id: int, db: Session = Depends(get_db)):
    """Belirli bir hattın detaylarını getir"""
    route = db.query(TransportRoute).filter(TransportRoute.id == route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    try:
        departure_times = json.loads(route.departure_times)
        active_days = json.loads(route.active_days)
    except:
        departure_times = []
        active_days = [0, 1, 2, 3, 4, 5, 6]
    
    # Bir sonraki otobüsü hesapla
    next_bus = calculate_next_bus(route)
    
    return {
        "id": route.id,
        "route_number": route.route_number,
        "route_name": route.route_name,
        "departure_location": route.departure_location,
        "arrival_location": route.arrival_location,
        "departure_times": departure_times,
        "active_days": active_days,
        "next_bus": next_bus
    }

@router.post("/transport/alarms", tags=["transport"])
async def create_alarm(
    alarm_data: AlarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Yeni alarm oluştur"""
    # Route var mı kontrol et
    route = db.query(TransportRoute).filter(TransportRoute.id == alarm_data.route_id).first()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # Aynı rota için zaten alarm var mı kontrol et
    existing_alarm = db.query(UserTransportAlarm).filter(
        UserTransportAlarm.user_id == current_user.id,
        UserTransportAlarm.route_id == alarm_data.route_id
    ).first()
    
    if existing_alarm:
        raise HTTPException(status_code=400, detail="Alarm already exists for this route")
    
    # Yeni alarm oluştur
    new_alarm = UserTransportAlarm(
        user_id=current_user.id,
        route_id=alarm_data.route_id,
        travel_time_to_stop=alarm_data.travel_time_to_stop,
        notification_minutes_before=alarm_data.notification_minutes_before,
        alarm_enabled=1
    )
    
    db.add(new_alarm)
    db.commit()
    db.refresh(new_alarm)
    
    return {
        "id": new_alarm.id,
        "route_id": new_alarm.route_id,
        "travel_time_to_stop": new_alarm.travel_time_to_stop,
        "alarm_enabled": bool(new_alarm.alarm_enabled),
        "notification_minutes_before": new_alarm.notification_minutes_before
    }

@router.get("/transport/alarms", tags=["transport"])
async def get_alarms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının aktif alarmlarını getir"""
    alarms_data = get_user_alarms_with_next_buses(db, current_user.id)
    return alarms_data

@router.put("/transport/alarms/{alarm_id}", tags=["transport"])
async def update_alarm(
    alarm_id: int,
    alarm_data: AlarmUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alarm güncelle"""
    alarm = db.query(UserTransportAlarm).filter(
        UserTransportAlarm.id == alarm_id,
        UserTransportAlarm.user_id == current_user.id
    ).first()
    
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    # Güncelleme
    if alarm_data.travel_time_to_stop is not None:
        alarm.travel_time_to_stop = alarm_data.travel_time_to_stop
    if alarm_data.notification_minutes_before is not None:
        alarm.notification_minutes_before = alarm_data.notification_minutes_before
    if alarm_data.alarm_enabled is not None:
        alarm.alarm_enabled = 1 if alarm_data.alarm_enabled else 0
    
    alarm.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alarm)
    
    return {
        "id": alarm.id,
        "route_id": alarm.route_id,
        "travel_time_to_stop": alarm.travel_time_to_stop,
        "alarm_enabled": bool(alarm.alarm_enabled),
        "notification_minutes_before": alarm.notification_minutes_before
    }

@router.delete("/transport/alarms/{alarm_id}", tags=["transport"])
async def delete_alarm(
    alarm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alarm sil"""
    alarm = db.query(UserTransportAlarm).filter(
        UserTransportAlarm.id == alarm_id,
        UserTransportAlarm.user_id == current_user.id
    ).first()
    
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm not found")
    
    db.delete(alarm)
    db.commit()
    
    return {"message": "Alarm deleted successfully"}

@router.get("/transport/next-buses", tags=["transport"])
async def get_next_buses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Kullanıcının alarmlarına göre gelecek otobüsleri getir"""
    alarms_data = get_user_alarms_with_next_buses(db, current_user.id)
    return alarms_data
