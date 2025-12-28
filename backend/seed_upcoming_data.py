import datetime
import sys
import os

# PYTHONPATH ayarı
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import UpcomingEvent

def seed_upcoming():
    db = SessionLocal()
    # Mevcutları çekmeyelim, temizleyelim veya sadece ekleyelim.
    # Burada sadece ekleyelim.
    
    events = [
        {
            "title": "ABD Kritik Seçim Süreci",
            "description": "ABD'de gerçekleşecek olan yerel/ara seçimler piyasalarda belirsizliği artırıyor.",
            "event_date": datetime.datetime(2026, 1, 24),
            "category": "politik",
            "impact_prediction": "Altında Yükseliş Beklentisi",
            "ai_advice": "Kaggle verilerine göre: Geçmişteki benzer ABD seçim belirsizliklerinde altın fiyatları 1 ay içinde ortalama %3.8 değer kazanmıştır. 24 Ocak yaklaşırken pozisyonlar gözden geçirilmeli."
        },
        {
            "title": "FED Faiz Kararı",
            "description": "Yılın ilk büyük faiz kararı. Piyasalar faiz indirimi veya sabit bırakma beklentisinde.",
            "event_date": datetime.datetime(2026, 2, 1),
            "category": "ekonomik",
            "impact_prediction": "Dolar/TL Volatilitesi",
            "ai_advice": "Tarihsel analizler, FED'in faiz artırım döngüsü sonlarında gelişmekte olan ülke para birimlerinin (TRY dahil) kısa süreli rahatlama yaşadığını gösteriyor."
        },
        {
            "title": "Küresel Teknoloji Zirvesi",
            "description": "Yapay zeka ve yeni ekonomik modellerin tartışılacağı dev zirve.",
            "event_date": datetime.datetime(2026, 1, 15),
            "category": "teknoloji",
            "impact_prediction": "Borsa İstanbul Teknoloji Endeksi Etkisi",
            "ai_advice": "Bu tür zirveler sonrası teknoloji hisselerinde hacim artışı gözlemleniyor. BIST Tech endeksi takip edilebilir."
        }
    ]
    
    # Eskileri silelim ki temiz olsun
    db.query(UpcomingEvent).delete()
    
    for e_data in events:
        event = UpcomingEvent(**e_data)
        db.add(event)
    
    db.commit()
    db.close()
    print("Gelecek olaylar başarıyla yüklendi!")

if __name__ == "__main__":
    seed_upcoming()
