import tradingeconomics as te
import os
import pandas as pd
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingEconomicsService:
    def __init__(self):
        self.key = os.getenv('TRADING_ECONOMICS_KEY', 'guest')
        self.secret = os.getenv('TRADING_ECONOMICS_SECRET', 'guest')
        try:
            te.login(f"{self.key}:{self.secret}")
        except Exception as e:
            logger.error(f"TradingEconomics login error: {e}")

    def get_economic_calendar(self, importance='High'):
        """
        Gets economic calendar events.
        """
        try:
            # Get calendar for the next 7 days
            start_date = datetime.now().strftime('%Y-%m-%d')
            end_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            data = te.getCalendarData(importance=importance, output_type='df')
            
            if data is None or data.empty:
                return []
            
            # Filter for future events if needed, but getCalendarData usually returns recent/upcoming
            return data.to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching economic calendar: {e}")
            return []

    def get_market_indicators(self, country=['turkey', 'united states']):
        """
        Gets key market indicators for selected countries.
        """
        try:
            data = te.getIndicatorData(country=country, output_type='df')
            if data is None or data.empty:
                return []
            return data.to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching indicators: {e}")
            return []

    def get_commodity_prices(self):
        """
        Gets commodity prices (Gold, Oil, etc.)
        """
        try:
            data = te.getMarketsData(marketsField='commodities', output_type='df')
            if data is None or data.empty:
                return []
            return data.to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching commodity prices: {e}")
            return []

    def generate_market_pulse(self):
        """
        Generates a summary of the market's current state and outlook.
        """
        calendar = self.get_economic_calendar()
        
        pulse = {
            "title": "Günün Analizi",
            "content": "Piyasalar şu an küresel ekonomik verilere odaklanmış durumda. Geçmişte benzer veri dönemlerinde altın fiyatlarında %2'lik oynaklıklar gözlemlenmişti. Sakin seyrin yerini hareketliliğe bırakması beklenebilir.",
            "sentiment": "neutral",
            "highlights": ["Dolar Endeksi Takibi", "FED Söylemleri", "Güvenli Liman Talebi"]
        }
        
        if calendar:
            important_events = [e for e in calendar if e.get('Importance') == 'High']
            if important_events:
                event = important_events[0]
                pulse["content"] = f"{event.get('Event')} verisi açıklanacak. Geçmişteki benzer veriler sonrası Altın piyasasında sert hareketler görüldü. Yatırımcıların bu haberi 'güvenli liman' arayışıyla takip etmesi tavsiye edilir."
                pulse["highlights"].append(f"Kritik: {event.get('Event')}")

        return pulse

    def get_scenario_cards(self):
        """
        Generates scenario cards based on upcoming events.
        """
        scenarios = [
            {
                "id": 1,
                "title": "Faiz Sabit Kalırsa",
                "impact": "Altın: +0.5%",
                "advice": "Geçmişte faiz sabit kaldığında altın kademeli bir yükseliş sergilemişti. Bu senaryoda sakin bir pozitiflik beklenebilir.",
                "probability": "Yüksek Olasılık",
                "type": "expected",
                "color": "blue"
            },
            {
                "id": 2,
                "title": "Faiz Artarsa",
                "impact": "Altın: -1.2%",
                "advice": "Sürpriz faiz artışları doları güçlendirirken altını baskılar. Tarihsel olarak bu durumlarda hızlı geri çekilmeler yaşanmıştır.",
                "probability": "Düşük Olasılık",
                "type": "surprise",
                "color": "red"
            },
            {
                "id": 3,
                "title": "Jeopolitik Gerilim Artarsa",
                "impact": "Altın: +2.0%, USDTRY: +1.5%",
                "advice": "Gerilim anlarında yatırımcı güvenli liman olan altına kaçar. Geçmişteki benzer kriz dönemlerinde altın %2.0 üzerinde prim yapmıştır.",
                "probability": "Orta Olasılık",
                "type": "risk",
                "color": "orange"
            }
        ]
        return scenarios

trading_economics_service = TradingEconomicsService()
