import pandas as pd
import yfinance as yf
from database import engine, SessionLocal
from models import CurrentMarketRate, CurrentEvent
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_correlation(asset1: str, asset2: str):
    query = f"""
    SELECT time, symbol, price 
    FROM market_data 
    WHERE symbol IN ('{asset1}', '{asset2}') 
    ORDER BY time ASC
    """
    
    try:
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return {"error": "No data found"}
            
        # Pivot to get columns for each symbol
        df_pivot = df.pivot(index='time', columns='symbol', values='price')
        
        # Calculate correlation
        correlation = df_pivot[asset1].corr(df_pivot[asset2])
        
        insight = ""
        if correlation > 0.7:
            insight = f"Güçlü pozitif ilişki. {asset1} arttığında, {asset2} genellikle onu takip eder."
        elif correlation < -0.7:
            insight = f"Güçlü ters ilişki. {asset1} arttığında, {asset2} düşer."
        else:
            insight = "Güçlü bir korelasyon tespit edilmedi."
            
        return {
            "asset1": asset1,
            "asset2": asset2,
            "correlation_score": round(correlation, 4),
            "insight": insight,
            "data_points": len(df_pivot)
        }
        
    except Exception as e:
        return {"error": str(e)}


async def get_current_rates(symbols=None):
    """
    Database'deki güncel kurları döndürür.
    (Canlı veri çekme işi scheduler.py içindeki fetch_market_data'ya bırakıldı)
    """
    if symbols is None:
        symbols = ['GOLD', 'USDTRY']
    
    db = SessionLocal()
    rates_data = []
    
    try:
        rates = db.query(CurrentMarketRate).filter(CurrentMarketRate.symbol.in_(symbols)).all()
        
        for rate in rates:
            rates_data.append({
                'symbol': rate.symbol,
                'name': rate.name,
                'price': float(rate.price),
                'daily_change': float(rate.daily_change),
                'daily_change_percent': float(rate.daily_change_percent),
                'last_updated': rate.last_updated.isoformat() if rate.last_updated else None
            })
        
        return rates_data
        
    except Exception as e:
        logger.error(f"Kur getirme hatası: {str(e)}")
        return []
    finally:
        db.close()


async def get_market_analysis():
    """
    Komple piyasa analizi döndürür:
    - Güncel kurlar
    - Güncel olaylar ve tahminleri
    - Genel durum özeti
    """
    db = SessionLocal()
    
    try:
        # Önce kurları güncelle
        await get_current_rates()
        
        # Güncel kurları al
        rates = db.query(CurrentMarketRate).all()
        
        # Son güncel olayları al (en yüksek impact'e göre)
        recent_events = db.query(CurrentEvent).filter(
            CurrentEvent.analyzed == 1
        ).order_by(
            CurrentEvent.predicted_impact.desc()
        ).limit(5).all()
        
        # Formatla
        rates_data = []
        for rate in rates:
            rates_data.append({
                'symbol': rate.symbol,
                'name': rate.name,
                'price': round(rate.price, 2),
                'daily_change': round(rate.daily_change, 2),
                'daily_change_percent': round(rate.daily_change_percent, 2),
                'last_updated': rate.last_updated.isoformat() if rate.last_updated else None
            })
        
        events_data = []
        for event in recent_events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'category': event.category,
                'predicted_impact': round(event.predicted_impact, 2),
                'published_at': event.published_at.isoformat() if event.published_at else None,
                'url': event.url
            })
        
        # Genel durum özeti
        avg_impact = sum([e.predicted_impact for e in recent_events]) / len(recent_events) if recent_events else 0
        
        summary = "Piyasalar normal seyrinde" if avg_impact < 3 else \
                  "Orta seviye volatilite bekleniyor" if avg_impact < 6 else \
                  "Yüksek volatilite bekleniyor"
        
        return {
            'rates': rates_data,
            'events': events_data,
            'summary': summary,
            'avg_predicted_impact': round(avg_impact, 2),
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market analizi hatası: {str(e)}")
        return {
            'error': str(e),
            'rates': [],
            'events': []
        }
    finally:
        db.close()

