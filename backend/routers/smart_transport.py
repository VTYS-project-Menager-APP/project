"""
Smart Transport API Router
Akıllı ulaşım alarm sistemi için API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from database import get_db
from models import User, UserTransportAlarm, AlarmSelectedRoute
from auth_utils import get_current_user
from services.smart_transport_service import get_smart_transport_service
from services.ibb_transport_service import get_ibb_service

router = APIRouter(prefix="/transport/smart", tags=["smart-transport"])


# Pydantic Models
class SmartAlarmCreate(BaseModel):
    """Akıllı alarm oluşturma request"""
    alarm_name: str = Field(..., description="Alarm adı (örn: 'İşe Gidiş')")
    origin_location: str = Field(..., description="Başlangıç konumu")
    destination_location: str = Field(..., description="Hedef konum")
    target_arrival_time: str = Field(..., pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$", description="Varış saati (HH:MM)")
    travel_time_to_stop: int = Field(10, ge=1, le=60, description="Durağa yürüme süresi (dakika)")
    selected_hat_kodlari: List[str] = Field(..., min_items=1, description="Seçilen otobüs hatları")
    origin_durak_kodu: Optional[str] = Field(None, description="Başlangıç durak kodu")
    destination_durak_kodu: Optional[str] = Field(None, description="Hedef durak kodu")


class SmartAlarmUpdate(BaseModel):
    """Akıllı alarm güncelleme request"""
    alarm_name: Optional[str] = None
    origin_location: Optional[str] = None
    destination_location: Optional[str] = None
    target_arrival_time: Optional[str] = Field(None, pattern=r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
    travel_time_to_stop: Optional[int] = Field(None, ge=1, le=60)
    alarm_enabled: Optional[bool] = None


class RouteAddRequest(BaseModel):
    """Alarma hat ekleme request"""
    hat_kodu: str
    hat_adi: Optional[str] = None


class RouteSearchRequest(BaseModel):
    """Hat arama request"""
    origin_durak_kodu: str
    destination_durak_kodu: str


class AlarmStatusResponse(BaseModel):
    """Alarm durum response"""
    alarm_id: int
    alarm_name: str
    origin: str
    destination: str
    target_arrival_time: str
    travel_time_to_stop: int
    routes: List[dict]
    status: str
    message: str
    should_trigger: bool
    alarm_enabled: bool


# Endpoints

@router.post("/alarms", status_code=201)
async def create_smart_alarm(
    alarm_data: SmartAlarmCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Yeni akıllı alarm oluştur
    
    Kullanıcı hedef varış saati ve kullanacağı otobüs hatlarını seçer.
    Sistem otomatik olarak doğru zamanda alarm tetikler.
    """
    smart_service = get_smart_transport_service()
    
    try:
        alarm = await smart_service.create_smart_alarm(
            db=db,
            user_id=current_user.id,
            alarm_name=alarm_data.alarm_name,
            origin_location=alarm_data.origin_location,
            destination_location=alarm_data.destination_location,
            target_arrival_time=alarm_data.target_arrival_time,
            travel_time_to_stop=alarm_data.travel_time_to_stop,
            selected_hat_kodlari=alarm_data.selected_hat_kodlari,
            origin_durak_kodu=alarm_data.origin_durak_kodu,
            destination_durak_kodu=alarm_data.destination_durak_kodu
        )
        
        return {
            "id": alarm.id,
            "alarm_name": alarm.alarm_name,
            "message": f"'{alarm.alarm_name}' alarmı başarıyla oluşturuldu!"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alarm oluşturma hatası: {str(e)}")


@router.get("/alarms", response_model=List[AlarmStatusResponse])
async def get_user_alarms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Kullanıcının tüm alarmlarını ve durumlarını getir
    
    Her alarm için:
    - Seçili hatlar
    - Tetiklenme durumu
    - Kalan süre mesajı
    """
    smart_service = get_smart_transport_service()
    
    try:
        alarms_status = await smart_service.get_user_active_alarms_status(
            db=db,
            user_id=current_user.id
        )
        return alarms_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alarm listesi hatası: {str(e)}")


@router.get("/alarms/{alarm_id}")
async def get_alarm_detail(
    alarm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Belirli bir alarmın detaylarını getir"""
    alarm = db.query(UserTransportAlarm).filter(
        UserTransportAlarm.id == alarm_id,
        UserTransportAlarm.user_id == current_user.id
    ).first()
    
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm bulunamadı")
    
    # Seçili hatları getir
    routes = db.query(AlarmSelectedRoute).filter(
        AlarmSelectedRoute.alarm_id == alarm_id,
        AlarmSelectedRoute.is_active == 1
    ).all()
    
    return {
        "id": alarm.id,
        "alarm_name": alarm.alarm_name,
        "origin_location": alarm.origin_location,
        "destination_location": alarm.destination_location,
        "origin_durak_kodu": alarm.origin_durak_kodu,
        "destination_durak_kodu": alarm.destination_durak_kodu,
        "target_arrival_time": alarm.target_arrival_time,
        "travel_time_to_stop": alarm.travel_time_to_stop,
        "alarm_enabled": bool(alarm.alarm_enabled),
        "routes": [
            {
                "id": r.id,
                "hat_kodu": r.hat_kodu,
                "hat_adi": r.hat_adi,
                "priority": r.priority
            } for r in routes
        ],
        "created_at": alarm.created_at,
        "last_triggered": alarm.last_triggered
    }


@router.put("/alarms/{alarm_id}")
async def update_alarm(
    alarm_id: int,
    alarm_data: SmartAlarmUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alarm güncelle"""
    alarm = db.query(UserTransportAlarm).filter(
        UserTransportAlarm.id == alarm_id,
        UserTransportAlarm.user_id == current_user.id
    ).first()
    
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm bulunamadı")
    
    # Güncelleme
    if alarm_data.alarm_name is not None:
        alarm.alarm_name = alarm_data.alarm_name
    if alarm_data.origin_location is not None:
        alarm.origin_location = alarm_data.origin_location
    if alarm_data.destination_location is not None:
        alarm.destination_location = alarm_data.destination_location
    if alarm_data.target_arrival_time is not None:
        alarm.target_arrival_time = alarm_data.target_arrival_time
    if alarm_data.travel_time_to_stop is not None:
        alarm.travel_time_to_stop = alarm_data.travel_time_to_stop
    if alarm_data.alarm_enabled is not None:
        alarm.alarm_enabled = 1 if alarm_data.alarm_enabled else 0
    
    alarm.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alarm)
    
    return {
        "id": alarm.id,
        "message": "Alarm başarıyla güncellendi"
    }


@router.delete("/alarms/{alarm_id}")
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
        raise HTTPException(status_code=404, detail="Alarm bulunamadı")
    
    db.delete(alarm)
    db.commit()
    
    return {"message": "Alarm başarıyla silindi"}


@router.post("/alarms/{alarm_id}/routes")
async def add_route_to_alarm(
    alarm_id: int,
    route_data: RouteAddRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alarma yeni hat ekle"""
    # Alarm kontrolü
    alarm = db.query(UserTransportAlarm).filter(
        UserTransportAlarm.id == alarm_id,
        UserTransportAlarm.user_id == current_user.id
    ).first()
    
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm bulunamadı")
    
    smart_service = get_smart_transport_service()
    
    try:
        route = await smart_service.add_route_to_alarm(
            db=db,
            alarm_id=alarm_id,
            hat_kodu=route_data.hat_kodu,
            hat_adi=route_data.hat_adi
        )
        
        return {
            "id": route.id,
            "hat_kodu": route.hat_kodu,
            "message": f"{route.hat_kodu} hattı alarma eklendi"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hat ekleme hatası: {str(e)}")


@router.delete("/alarms/{alarm_id}/routes/{hat_kodu}")
async def remove_route_from_alarm(
    alarm_id: int,
    hat_kodu: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alarmdan hat çıkar"""
    # Alarm kontrolü
    alarm = db.query(UserTransportAlarm).filter(
        UserTransportAlarm.id == alarm_id,
        UserTransportAlarm.user_id == current_user.id
    ).first()
    
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm bulunamadı")
    
    smart_service = get_smart_transport_service()
    
    success = await smart_service.remove_route_from_alarm(
        db=db,
        alarm_id=alarm_id,
        hat_kodu=hat_kodu
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Hat bulunamadı")
    
    return {"message": f"{hat_kodu} hattı alarmdan çıkarıldı"}


@router.post("/routes/search")
async def search_routes_between_locations(
    search_data: RouteSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    İki durak arasındaki tüm otobüs hatlarını bul
    
    İBB API'yi kullanarak her iki duraktan da geçen hatları listeler
    """
    smart_service = get_smart_transport_service()
    
    try:
        routes = await smart_service.find_routes_between_locations(
            origin_durak=search_data.origin_durak_kodu,
            destination_durak=search_data.destination_durak_kodu
        )
        
        return {
            "origin_durak": search_data.origin_durak_kodu,
            "destination_durak": search_data.destination_durak_kodu,
            "routes": routes
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rota arama hatası: {str(e)}")


@router.get("/durak/{durak_kodu}/hatlar")
async def get_routes_by_stop(
    durak_kodu: str,
    current_user: User = Depends(get_current_user)
):
    """Belirli bir duraktan geçen tüm hatları getir"""
    ibb_service = get_ibb_service()
    
    try:
        hatlar = await ibb_service.get_duraktan_gecen_hatlar(durak_kodu)
        
        if hatlar is None:
            raise HTTPException(status_code=404, detail="Durak bulunamadı veya API hatası")
        
        return {
            "durak_kodu": durak_kodu,
            "hatlar": hatlar
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Durak hatları hatası: {str(e)}")


@router.get("/check-active")
async def check_active_alarms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """
    Aktif alarmları kontrol et ve tetiklenmesi gerekenleri döndür
    
    Bu endpoint frontend tarafından periyodik olarak çağrılır
    """
    smart_service = get_smart_transport_service()
    
    try:
        alarms_status = await smart_service.get_user_active_alarms_status(
            db=db,
            user_id=current_user.id
        )
        
        # Tetiklenmesi gereken alarmları filtrele
        triggered_alarms = [
            alarm for alarm in alarms_status 
            if alarm['should_trigger']
        ]
        
        return {
            "total_alarms": len(alarms_status),
            "triggered_alarms": triggered_alarms,
            "has_active_trigger": len(triggered_alarms) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alarm kontrolü hatası: {str(e)}")

