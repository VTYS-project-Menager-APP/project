"""
Market Analysis Router - API Endpoints
Piyasa analizi, güncel kurlar ve olay tahminleri için endpoint'ler
"""

from fastapi import APIRouter, HTTPException
from services.finance_service import get_current_rates, get_market_analysis
from services.news_service import news_service
from services.prediction_service import prediction_service
from services.trading_economics_service import trading_economics_service
import pandas as pd
from database import SessionLocal
from models import CurrentEvent, HistoricalEvent, MarketEventCorrelation, UpcomingEvent
from typing import List, Optional

router = APIRouter(
    prefix="/market-analysis",
    tags=["market-analysis"]
)


@router.get("/current-rates")
async def get_rates():
    """
    Güncel altın ve dolar kurlarını döndürür
    """
    try:
        rates_data = await get_current_rates(['GOLD', 'USDTRY'])
        
        return {
            'success': True,
            'data': rates_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current-events")
async def get_current_events(limit: int = 10):
    """
    Analiz edilmiş güncel olayları döndürür
    """
    db = SessionLocal()
    try:
        events = db.query(CurrentEvent).filter(
            CurrentEvent.analyzed == 1
        ).order_by(
            CurrentEvent.predicted_impact.desc()
        ).limit(limit).all()
        
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'category': event.category,
                'predicted_impact': round(event.predicted_impact, 2),
                'published_at': event.published_at.isoformat() if event.published_at else None,
                'url': event.url,
                'source': event.source
            })
        
        return {
            'success': True,
            'data': events_data,
            'count': len(events_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/full-analysis")
async def get_full_analysis():
    """
    Komple piyasa analizi: kurlar + olaylar + tahminler + özet
    """
    try:
        analysis = await get_market_analysis()
        
        return {
            'success': True,
            'data': analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical-correlation")
async def get_historical_correlation(
    category: Optional[str] = None,
    symbol: Optional[str] = 'GOLD',
    limit: int = 10
):
    """
    Geçmiş olay-piyasa korelasyonlarını döndürür
    """
    db = SessionLocal()
    try:
        query = db.query(
            HistoricalEvent, MarketEventCorrelation
        ).join(
            MarketEventCorrelation,
            HistoricalEvent.id == MarketEventCorrelation.event_id
        )
        
        if category:
            query = query.filter(HistoricalEvent.category == category)
        
        if symbol:
            query = query.filter(MarketEventCorrelation.symbol == symbol)
        
        results = query.order_by(
            HistoricalEvent.event_date.desc()
        ).limit(limit).all()
        
        data = []
        for event, correlation in results:
            data.append({
                'event_title': event.title,
                'event_date': event.event_date.isoformat() if event.event_date else None,
                'category': event.category,
                'impact_score': event.impact_score,
                'symbol': correlation.symbol,
                'price_before': correlation.price_before,
                'price_after': correlation.price_after,
                'percent_change': round(correlation.percent_change, 2),
                'correlation_strength': correlation.correlation_strength,
                'insight': prediction_service.generate_narrative(event.title, correlation.percent_change, correlation.symbol)
            })
        
        return {
            'success': True,
            'data': data,
            'count': len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/analyze-event")
async def analyze_specific_event(event_id: int):
    """
    Belirli bir olayı analiz eder ve tahmin yapar
    """
    db = SessionLocal()
    try:
        event = db.query(CurrentEvent).filter(CurrentEvent.id == event_id).first()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Her iki piyasa için tahmin
        predictions = {}
        for symbol in ['GOLD', 'USDTRY']:
            pred = prediction_service.predict_impact(event, symbol)
            predictions[symbol] = pred
        
        # En yüksek etkiyi kaydet
        max_impact = max(predictions['GOLD']['predicted_impact'], 
                        predictions['USDTRY']['predicted_impact'])
        
        event.predicted_impact = max_impact
        event.analyzed = 1
        db.commit()
        
        return {
            'success': True,
            'event': {
                'id': event.id,
                'title': event.title,
                'category': event.category
            },
            'predictions': predictions
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/top-impact-events")
async def get_top_impact(limit: int = 5):
    """
    En yüksek etkili olayları döndürür
    """
    try:
        events = prediction_service.get_top_impact_events(limit)
        
        data = []
        for event in events:
            data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'category': event.category,
                'predicted_impact': round(event.predicted_impact, 2),
                'published_at': event.published_at.isoformat() if event.published_at else None,
                'url': event.url
            })
        
        return {
            'success': True,
            'data': data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-news")
async def refresh_news():
    """
    Haberleri manuel olarak yeniler ve analiz eder
    """
    try:
        # Haberleri çek
        count = news_service.update_all_news()
        
        # Analiz et
        analyzed = prediction_service.analyze_all_pending_events()
        
        return {
            'success': True,
            'news_fetched': count,
            'events_analyzed': analyzed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/upcoming-events")
async def get_upcoming_events(limit: int = 5):
    """
    Beklenen gelecek olayları ve AI tavsiyelerini döndürür
    """
    db = SessionLocal()
    try:
        events = db.query(UpcomingEvent).order_by(
            UpcomingEvent.event_date.asc()
        ).limit(limit).all()
        
        data = []
        for event in events:
            data.append({
                'id': event.id,
                'title': event.title,
                'description': event.description,
                'event_date': event.event_date.isoformat(),
                'category': event.category,
                'impact_prediction': event.impact_prediction,
                'ai_advice': event.ai_advice
            })
        
        return {
            'success': True,
            'data': data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/market-pulse")
async def get_market_pulse():
    """
    Piyasa Nabzı - Özet ve Önemli Veriler
    """
    try:
        pulse = trading_economics_service.generate_market_pulse()
        return {
            'success': True,
            'data': pulse
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scenarios")
async def get_scenarios():
    """
    Olası Senaryolar ve Etkileri
    """
    try:
        scenarios = trading_economics_service.get_scenario_cards()
        return {
            'success': True,
            'data': scenarios
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
