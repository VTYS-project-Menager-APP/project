"""
Smart Transport Alarm Service
Akıllı ulaşım alarm sistemi - IBB API entegrasyonu ile gerçek zamanlı alarm yönetimi
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models import UserTransportAlarm, AlarmSelectedRoute, TransportRoute
from services.ibb_transport_service import get_ibb_service
import logging

logger = logging.getLogger(__name__)


class SmartTransportService:
    """Akıllı ulaşım alarm servisi"""
    
    def __init__(self):
        self.ibb_service = get_ibb_service()
    
    async def create_smart_alarm(
        self,
        db: Session,
        user_id: int,
        alarm_name: str,
        origin_location: str,
        destination_location: str,
        target_arrival_time: str,
        travel_time_to_stop: int,
        selected_hat_kodlari: List[str],
        origin_durak_kodu: Optional[str] = None,
        destination_durak_kodu: Optional[str] = None
    ) -> UserTransportAlarm:
        """
        Yeni akıllı alarm oluştur
        
        Args:
            db: Database session
            user_id: Kullanıcı ID
            alarm_name: Alarm adı (örn: "İşe Gidiş")
            origin_location: Başlangıç konumu
            destination_location: Hedef konum
            target_arrival_time: Varış saati (HH:MM)
            travel_time_to_stop: Durağa yürüme süresi (dakika)
            selected_hat_kodlari: Seçilen otobüs hatları listesi
            origin_durak_kodu: Başlangıç durak kodu (opsiyonel)
            destination_durak_kodu: Hedef durak kodu (opsiyonel)
        
        Returns:
            Oluşturulan alarm
        """
        # Yeni alarm oluştur
        new_alarm = UserTransportAlarm(
            user_id=user_id,
            alarm_name=alarm_name,
            origin_location=origin_location,
            destination_location=destination_location,
            origin_durak_kodu=origin_durak_kodu,
            destination_durak_kodu=destination_durak_kodu,
            target_arrival_time=target_arrival_time,
            travel_time_to_stop=travel_time_to_stop,
            alarm_enabled=1,
            notification_minutes_before=5
        )
        
        db.add(new_alarm)
        db.flush()  # ID'yi almak için
        
        # Seçilen hatları ekle
        for priority, hat_kodu in enumerate(selected_hat_kodlari):
            selected_route = AlarmSelectedRoute(
                alarm_id=new_alarm.id,
                hat_kodu=hat_kodu,
                priority=priority,
                is_active=1
            )
            db.add(selected_route)
        
        db.commit()
        db.refresh(new_alarm)
        
        logger.info(f"Akıllı alarm oluşturuldu: {alarm_name} (ID: {new_alarm.id})")
        return new_alarm
    
    async def check_alarm_should_trigger(
        self,
        db: Session,
        alarm: UserTransportAlarm,
        current_time: Optional[datetime] = None
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Alarmın tetiklenmesi gerekip gerekmediğini kontrol et
        
        Returns:
            (should_trigger: bool, alarm_data: dict | None)
        """
        if not alarm.alarm_enabled or not alarm.target_arrival_time:
            return False, None
        
        if current_time is None:
            current_time = datetime.now()
        
        # Hedef varış saatini parse et
        try:
            target_hour, target_minute = map(int, alarm.target_arrival_time.split(':'))
            today = current_time.date()
            target_arrival = datetime.combine(
                today,
                datetime.min.time().replace(hour=target_hour, minute=target_minute)
            )
        except:
            logger.error(f"Geçersiz hedef varış saati: {alarm.target_arrival_time}")
            return False, None
        
        # Geçmiş bir saat ise bugün için tetiklenmesin
        if target_arrival < current_time:
            return False, None
        
        # Seçili hatları al
        selected_routes = db.query(AlarmSelectedRoute).filter(
            and_(
                AlarmSelectedRoute.alarm_id == alarm.id,
                AlarmSelectedRoute.is_active == 1
            )
        ).all()
        
        if not selected_routes:
            logger.warning(f"Alarm {alarm.id} için seçili hat bulunamadı")
            return False, None
        
        # Her hat için kontrol et
        for route in selected_routes:
            try:
                # IBB API'den sefer bilgilerini al
                alarm_data = await self.ibb_service.calculate_smart_alarm_time(
                    hat_kodu=route.hat_kodu,
                    hedef_varis_saati=alarm.target_arrival_time,
                    yurume_suresi_dakika=alarm.travel_time_to_stop
                )
                
                if alarm_data and alarm_data.get('should_trigger_now'):
                    # Bu hat için alarm tetiklenmeli
                    return True, {
                        'alarm_id': alarm.id,
                        'alarm_name': alarm.alarm_name,
                        'hat_kodu': route.hat_kodu,
                        'origin': alarm.origin_location,
                        'destination': alarm.destination_location,
                        'target_arrival': alarm.target_arrival_time,
                        'message': alarm_data.get('message'),
                        'bus_departure': alarm_data.get('bus_departure'),
                        'estimated_arrival': alarm_data.get('estimated_arrival'),
                        'minutes_until_alarm': alarm_data.get('minutes_until_alarm')
                    }
            except Exception as e:
                logger.error(f"Hat {route.hat_kodu} kontrolü başarısız: {e}")
                continue
        
        return False, None
    
    async def get_user_active_alarms_status(
        self,
        db: Session,
        user_id: int
    ) -> List[Dict]:
        """
        Kullanıcının aktif alarmlarını ve durumlarını getir
        
        Returns:
            [{
                'alarm': UserTransportAlarm,
                'routes': [AlarmSelectedRoute],
                'next_trigger': datetime | None,
                'status': 'waiting' | 'ready' | 'triggered',
                'message': str
            }]
        """
        alarms = db.query(UserTransportAlarm).filter(
            and_(
                UserTransportAlarm.user_id == user_id,
                UserTransportAlarm.alarm_enabled == 1
            )
        ).all()
        
        result = []
        current_time = datetime.now()
        
        for alarm in alarms:
            # Seçili hatları al
            selected_routes = db.query(AlarmSelectedRoute).filter(
                and_(
                    AlarmSelectedRoute.alarm_id == alarm.id,
                    AlarmSelectedRoute.is_active == 1
                )
            ).all()
            
            # Alarm durumunu kontrol et
            should_trigger, trigger_data = await self.check_alarm_should_trigger(
                db, alarm, current_time
            )
            
            if should_trigger:
                status = 'triggered'
                message = trigger_data.get('message', 'Çıkma zamanı!')
            else:
                # Bir sonraki tetiklenme zamanını hesapla
                status = 'waiting'
                message = self._calculate_next_trigger_message(alarm)
            
            result.append({
                'alarm_id': alarm.id,
                'alarm_name': alarm.alarm_name,
                'origin': alarm.origin_location,
                'destination': alarm.destination_location,
                'target_arrival_time': alarm.target_arrival_time,
                'travel_time_to_stop': alarm.travel_time_to_stop,
                'routes': [
                    {
                        'hat_kodu': r.hat_kodu,
                        'hat_adi': r.hat_adi,
                        'priority': r.priority
                    } for r in selected_routes
                ],
                'status': status,
                'message': message,
                'should_trigger': should_trigger,
                'alarm_enabled': bool(alarm.alarm_enabled)
            })
        
        return result
    
    def _calculate_next_trigger_message(self, alarm: UserTransportAlarm) -> str:
        """Bir sonraki tetiklenme için mesaj oluştur"""
        if not alarm.target_arrival_time:
            return "Hedef varış saati ayarlanmamış"
        
        try:
            target_hour, target_minute = map(int, alarm.target_arrival_time.split(':'))
            now = datetime.now()
            today = now.date()
            target_time = datetime.combine(
                today,
                datetime.min.time().replace(hour=target_hour, minute=target_minute)
            )
            
            # Eğer geçmişse yarın için hesapla
            if target_time < now:
                target_time = target_time + timedelta(days=1)
            
            time_diff = target_time - now
            hours = int(time_diff.total_seconds() / 3600)
            minutes = int((time_diff.total_seconds() % 3600) / 60)
            
            if hours > 0:
                return f"✅ {alarm.target_arrival_time} için hazır. {hours} saat {minutes} dakika sonra."
            else:
                return f"✅ {alarm.target_arrival_time} için hazır. {minutes} dakika sonra."
        except:
            return "Alarm aktif"
    
    async def find_routes_between_locations(
        self,
        origin_durak: str,
        destination_durak: str
    ) -> List[Dict]:
        """
        İki durak arasındaki tüm hatları bul
        
        Returns:
            [{
                'hat_kodu': str,
                'hat_adi': str
            }]
        """
        hat_kodlari = await self.ibb_service.find_routes_between_locations(
            origin_durak, destination_durak
        )
        
        return [{'hat_kodu': kod, 'hat_adi': kod} for kod in hat_kodlari]
    
    async def add_route_to_alarm(
        self,
        db: Session,
        alarm_id: int,
        hat_kodu: str,
        hat_adi: Optional[str] = None
    ) -> AlarmSelectedRoute:
        """Alarma yeni hat ekle"""
        # Öncelik sırasını belirle (en sonuncu)
        max_priority = db.query(AlarmSelectedRoute).filter(
            AlarmSelectedRoute.alarm_id == alarm_id
        ).count()
        
        new_route = AlarmSelectedRoute(
            alarm_id=alarm_id,
            hat_kodu=hat_kodu,
            hat_adi=hat_adi or hat_kodu,
            priority=max_priority,
            is_active=1
        )
        
        db.add(new_route)
        db.commit()
        db.refresh(new_route)
        
        return new_route
    
    async def remove_route_from_alarm(
        self,
        db: Session,
        alarm_id: int,
        hat_kodu: str
    ) -> bool:
        """Alarmdan hat çıkar"""
        route = db.query(AlarmSelectedRoute).filter(
            and_(
                AlarmSelectedRoute.alarm_id == alarm_id,
                AlarmSelectedRoute.hat_kodu == hat_kodu
            )
        ).first()
        
        if route:
            db.delete(route)
            db.commit()
            return True
        return False


# Global service instance
_smart_transport_service: Optional[SmartTransportService] = None

def get_smart_transport_service() -> SmartTransportService:
    """Global smart transport service instance"""
    global _smart_transport_service
    if _smart_transport_service is None:
        _smart_transport_service = SmartTransportService()
    return _smart_transport_service

