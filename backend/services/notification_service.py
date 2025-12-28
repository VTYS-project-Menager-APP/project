from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# In-memory bildirim deposu (gerçek uygulamada WebSocket veya Redis kullanılmalı)
pending_notifications = {}

def add_pending_notification(user_id: int, notification_data: Dict):
    """Bekleyen bildirim ekle"""
    if user_id not in pending_notifications:
        pending_notifications[user_id] = []
    
    pending_notifications[user_id].append({
        **notification_data,
        'timestamp': datetime.now(),
        'sent': False
    })
    
    logger.info(f"Notification added for user {user_id}: {notification_data}")

def get_pending_notifications(user_id: int) -> List[Dict]:
    """Kullanıcının bekleyen bildirimlerini getir"""
    if user_id not in pending_notifications:
        return []
    
    # Sadece gönderilmemiş bildirimleri döndür
    unsent = [n for n in pending_notifications[user_id] if not n.get('sent', False)]
    
    # Gönderilmiş olarak işaretle
    for notification in unsent:
        notification['sent'] = True
    
    return unsent

def clear_old_notifications(user_id: int):
    """Eski bildirimleri temizle"""
    if user_id in pending_notifications:
        # Son 10 bildirimi tut
        pending_notifications[user_id] = pending_notifications[user_id][-10:]

def send_alarm_notification(user_id: int, alarm_data: Dict):
    """
    Kullanıcıya alarm bildirimi gönder
    
    Args:
        user_id: Kullanıcı ID
        alarm_data: {
            'route_number': str,
            'route_name': str,
            'departure_location': str,
            'next_departure': datetime,
            'minutes_until_departure': int,
            'travel_time_to_stop': int,
            'can_catch_message': str
        }
    """
    notification = {
        'type': 'transport_alarm',
        'title': f"{alarm_data['route_number']} Numaralı Otobüs",
        'message': f"{alarm_data['route_number']} numaralı araç {alarm_data['departure_location']}'tan yola çıktı!",
        'action_message': alarm_data.get('can_catch_message', ''),
        'route_info': {
            'route_number': alarm_data['route_number'],
            'route_name': alarm_data['route_name'],
            'departure_location': alarm_data['departure_location'],
            'arrival_location': alarm_data.get('arrival_location', ''),
        },
        'timing': {
            'next_departure': alarm_data['next_departure'].isoformat(),
            'minutes_until_departure': alarm_data['minutes_until_departure'],
            'travel_time_to_stop': alarm_data['travel_time_to_stop']
        }
    }
    
    add_pending_notification(user_id, notification)
    
    return notification
