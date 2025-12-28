"""
Ulaşım hatları için örnek veri ekleyen script
"""
from database import SessionLocal
from models import TransportRoute
import json

def seed_transport_routes():
    db = SessionLocal()
    
    try:
        # Mevcut route sayısını kontrol et
        existing_count = db.query(TransportRoute).count()
        if existing_count > 0:
            print(f"Already have {existing_count} routes, skipping seed.")
            return
        
        # İstanbul örnek otobüs hatları
        routes = [
            {
                "route_number": "34",
                "route_name": "Kadıköy - Beylikdüzü",
                "departure_location": "Kadıköy",
                "arrival_location": "Beylikdüzü",
                "departure_times": json.dumps([
                    "06:00", "06:30", "07:00", "07:30", "08:00", "08:30",
                    "09:00", "09:30", "10:00", "11:00", "12:00", "13:00",
                    "14:00", "15:00", "16:00", "17:00", "17:30", "18:00",
                    "18:30", "19:00", "20:00", "21:00", "22:00"
                ]),
                "active_days": json.dumps([0, 1, 2, 3, 4, 5, 6])
            },
            {
                "route_number": "500T",
                "route_name": "Taksim - Sarıyer",
                "departure_location": "Taksim",
                "arrival_location": "Sarıyer",
                "departure_times": json.dumps([
                    "06:15", "06:45", "07:15", "07:45", "08:15", "08:45",
                    "09:15", "10:00", "11:00", "12:00", "13:00", "14:00",
                    "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"
                ]),
                "active_days": json.dumps([0, 1, 2, 3, 4, 5, 6])
            },
            {
                "route_number": "16D",
                "route_name": "Levent - Eminönü",
                "departure_location": "Levent",
                "arrival_location": "Eminönü",
                "departure_times": json.dumps([
                    "06:00", "06:20", "06:40", "07:00", "07:20", "07:40",
                    "08:00", "08:20", "08:40", "09:00", "09:30", "10:00",
                    "10:30", "11:00", "12:00", "13:00", "14:00", "15:00",
                    "16:00", "17:00", "17:20", "17:40", "18:00", "18:20",
                    "18:40", "19:00", "20:00", "21:00"
                ]),
                "active_days": json.dumps([0, 1, 2, 3, 4])  # Sadece hafta içi
            },
            {
                "route_number": "12B",
                "route_name": "Bakırköy - Beşiktaş",
                "departure_location": "Bakırköy",
                "arrival_location": "Beşiktaş",
                "departure_times": json.dumps([
                    "06:30", "07:00", "07:30", "08:00", "08:30", "09:00",
                    "10:00", "11:00", "12:00", "13:00", "14:00", "15:00",
                    "16:00", "17:00", "17:30", "18:00", "18:30", "19:00",
                    "20:00", "21:00"
                ]),
                "active_days": json.dumps([0, 1, 2, 3, 4, 5, 6])
            },
            {
                "route_number": "28",
                "route_name": "Beşiktaş - Edirnekapı",
                "departure_location": "Beşiktaş",
                "arrival_location": "Edirnekapı",
                "departure_times": json.dumps([
                    "06:00", "06:30", "07:00", "07:30", "08:00", "08:30",
                    "09:00", "09:30", "10:00", "11:00", "12:00", "13:00",
                    "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"
                ]),
                "active_days": json.dumps([0, 1, 2, 3, 4, 5, 6])
            },
            {
                "route_number": "41ST",
                "route_name": "Taksim - Topkapı",
                "departure_location": "Taksim",
                "arrival_location": "Topkapı",
                "departure_times": json.dumps([
                    "06:15", "06:45", "07:15", "07:45", "08:15", "08:45",
                    "09:15", "10:00", "11:00", "12:00", "13:00", "14:00",
                    "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"
                ]),
                "active_days": json.dumps([0, 1, 2, 3, 4, 5, 6])
            }
        ]
        
        for route_data in routes:
            route = TransportRoute(**route_data)
            db.add(route)
        
        db.commit()
        print(f"Successfully added {len(routes)} transport routes!")
        
    except Exception as e:
        print(f"Error seeding transport routes: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_transport_routes()
