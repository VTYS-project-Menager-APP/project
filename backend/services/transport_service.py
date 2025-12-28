from datetime import datetime, timedelta
from typing import List, Optional, Dict
import json
from sqlalchemy.orm import Session
from models import TransportRoute, UserTransportAlarm

def parse_departure_times(route: TransportRoute) -> List[str]:
    """Otobüs kalkış saatlerini parse et"""
    try:
        return json.loads(route.departure_times)
    except:
        return []

def calculate_next_bus(route: TransportRoute, current_time: datetime = None) -> Optional[Dict]:
    """
    Bir sonraki otobüs zamanını hesaplar
    
    Returns:
        dict: {
            'next_departure': datetime,
            'time_until_departure': timedelta,
            'minutes_until_departure': int
        }
    """
    if current_time is None:
        current_time = datetime.now()
    
    # Bugünün günü
    current_day = current_time.weekday()  # 0=Monday, 6=Sunday
    
    # Aktif günleri kontrol et
    try:
        active_days = json.loads(route.active_days)
        if current_day not in active_days:
            return None
    except:
        pass  # Hata varsa tüm günler aktif kabul et
    
    # Kalkış saatlerini parse et
    departure_times = parse_departure_times(route)
    if not departure_times:
        return None
    
    # Bugünün tarihi
    today = current_time.date()
    
    # Gelecekteki ilk kalkış saatini bul
    next_departures = []
    for time_str in departure_times:
        try:
            hour, minute = map(int, time_str.split(':'))
            departure_datetime = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            
            # Eğer bu saat geçmemişse ekle
            if departure_datetime > current_time:
                next_departures.append(departure_datetime)
        except:
            continue
    
    if not next_departures:
        return None
    
    # En yakın zamanı seç
    next_departure = min(next_departures)
    time_until = next_departure - current_time
    
    return {
        'next_departure': next_departure,
        'time_until_departure': time_until,
        'minutes_until_departure': int(time_until.total_seconds() / 60)
    }

def should_trigger_alarm(
    alarm: UserTransportAlarm, 
    route: TransportRoute,
    current_time: datetime = None
) -> tuple[bool, Optional[Dict]]:
    """
    Alarm tetiklenme durumunu kontrol eder
    
    Returns:
        tuple: (should_trigger: bool, alarm_data: dict | None)
    """
    if not alarm.alarm_enabled:
        return False, None
    
    if current_time is None:
        current_time = datetime.now()
    
    # Bir sonraki otobüsü hesapla
    next_bus = calculate_next_bus(route, current_time)
    if not next_bus:
        return False, None
    
    # Kullanıcının durağa varması gereken süre
    travel_time = alarm.travel_time_to_stop
    notification_before = alarm.notification_minutes_before
    
    # Total süre = durağa varış + ekstra bildirim süresi
    total_minutes_needed = travel_time + notification_before
    
    # Otobüse kadar kalan süre
    minutes_until_bus = next_bus['minutes_until_departure']
    
    # Alarm tetiklenmeli mi?
    # Eğer kalan süre, kullanıcının ihtiyaç duyduğu süreye eşit veya az ise tetikle
    should_trigger = minutes_until_bus <= total_minutes_needed and minutes_until_bus > 0
    
    if should_trigger:
        alarm_data = {
            'route_number': route.route_number,
            'route_name': route.route_name,
            'departure_location': route.departure_location,
            'arrival_location': route.arrival_location,
            'next_departure': next_bus['next_departure'],
            'minutes_until_departure': minutes_until_bus,
            'travel_time_to_stop': travel_time,
            'can_catch_message': f"{travel_time} dakika içinde çıkarsan otobüse yetişebilirsin!"
        }
        return True, alarm_data
    
    return False, None

def get_time_to_catch_bus(
    alarm: UserTransportAlarm, 
    next_bus_time: datetime,
    current_time: datetime = None
) -> int:
    """
    Otobüse yetişmek için kalan süreyi hesaplar
    
    Returns:
        int: Dakika cinsinden kalan süre
    """
    if current_time is None:
        current_time = datetime.now()
    
    time_until_bus = next_bus_time - current_time
    minutes_until = int(time_until_bus.total_seconds() / 60)
    
    # Kullanıcının durağa varma süresi
    travel_time = alarm.travel_time_to_stop
    
    # Çıkması gereken süre
    time_to_leave = minutes_until - travel_time
    
    return max(0, time_to_leave)

def get_user_alarms_with_next_buses(db: Session, user_id: int) -> List[Dict]:
    """
    Kullanıcının tüm alarmlarını ve bir sonraki otobüs bilgilerini getirir
    """
    alarms = db.query(UserTransportAlarm).filter(
        UserTransportAlarm.user_id == user_id,
        UserTransportAlarm.alarm_enabled == 1
    ).all()
    
    result = []
    current_time = datetime.now()
    
    for alarm in alarms:
        route = db.query(TransportRoute).filter(
            TransportRoute.id == alarm.route_id
        ).first()
        
        if not route:
            continue
        
        next_bus = calculate_next_bus(route, current_time)
        
        alarm_info = {
            'alarm_id': alarm.id,
            'route_id': route.id,
            'route_number': route.route_number,
            'route_name': route.route_name,
            'departure_location': route.departure_location,
            'arrival_location': route.arrival_location,
            'travel_time_to_stop': alarm.travel_time_to_stop,
            'next_bus': next_bus,
            'alarm_enabled': bool(alarm.alarm_enabled)
        }
        
        result.append(alarm_info)
    
    return result
