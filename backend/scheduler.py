from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import SessionLocal
from models import MarketData
import datetime
import random
import yfinance as yf
import pandas as pd

scheduler = AsyncIOScheduler()

async def fetch_market_data():
    """
    Fetch real market data using yfinance and update both history and current rates.
    """
    print("Fetching live market data...")
    db = SessionLocal()
    try:
        from models import CurrentMarketRate
        
        # Map symbols for internal use and yfinance
        symbol_map = {
            "USDTRY": "USDTRY=X",
            "GOLD": "GC=F" 
        }
        
        now = datetime.datetime.utcnow()
        
        for app_symbol, yf_symbol in symbol_map.items():
            try:
                ticker = yf.Ticker(yf_symbol)
                # Get 2 days of data to calculate daily change
                data = ticker.history(period="2d")
                
                if not data.empty:
                    current_price = data['Close'].iloc[-1]
                    previous_close = data['Close'].iloc[-2] if len(data) > 1 else current_price
                    
                    daily_change = current_price - previous_close
                    daily_change_percent = (daily_change / previous_close) * 100 if previous_close > 0 else 0
                    
                    # 1. Update MarketData (History)
                    new_history = MarketData(
                        time=now,
                        symbol="XAUUSD" if app_symbol == "GOLD" else app_symbol,
                        price=float(current_price),
                        volume=0
                    )
                    db.add(new_history)
                    
                    # 2. Update CurrentMarketRate (Live View)
                    rate = db.query(CurrentMarketRate).filter_by(symbol=app_symbol).first()
                    if rate:
                        rate.price = float(current_price)
                        rate.daily_change = float(daily_change)
                        rate.daily_change_percent = float(daily_change_percent)
                        rate.previous_close = float(previous_close)
                        rate.last_updated = now
                    else:
                        rate = CurrentMarketRate(
                            symbol=app_symbol,
                            name="Altın (Ons/USD)" if app_symbol == "GOLD" else "Dolar/TL",
                            price=float(current_price),
                            daily_change=float(daily_change),
                            daily_change_percent=float(daily_change_percent),
                            previous_close=float(previous_close),
                            last_updated=now
                        )
                        db.add(rate)
                        
            except Exception as e:
                print(f"Error updating {app_symbol}: {e}")
        
        db.commit()
        print("Market data and current rates updated successfully.")
    except Exception as e:
        print(f"Error in fetch_market_data: {e}")
    finally:
        db.close()


async def update_news_and_analyze():
    """
    Haberleri günceller ve analiz eder
    """
    print("Fetching latest news and analyzing events...")
    try:
        from services.news_service import news_service
        from services.prediction_service import prediction_service
        
        # Haberleri çek
        count = news_service.update_all_news()
        print(f"{count} yeni haber eklendi.")
        
        # Analiz et
        analyzed = prediction_service.analyze_all_pending_events()
        print(f"{analyzed} olay analiz edildi.")
        
    except Exception as e:
        print(f"News update/analysis error: {e}")


async def check_transport_alarms():
    """
    Aktif ulaşım alarmlarını kontrol eder ve gerekirse bildirim gönderir
    """
    print("Checking transport alarms...")
    db = SessionLocal()
    try:
        from models import UserTransportAlarm, TransportRoute
        from services.transport_service import should_trigger_alarm
        from services.notification_service import send_alarm_notification
        
        # Tüm aktif alarmları al
        active_alarms = db.query(UserTransportAlarm).filter(
            UserTransportAlarm.alarm_enabled == 1
        ).all()
        
        for alarm in active_alarms:
            # Route bilgisini al
            route = db.query(TransportRoute).filter(
                TransportRoute.id == alarm.route_id
            ).first()
            
            if not route:
                continue
            
            # Alarm tetiklenmeli mi kontrol et
            should_trigger, alarm_data = should_trigger_alarm(alarm, route)
            
            if should_trigger:
                # Bildirim gönder
                send_alarm_notification(alarm.user_id, alarm_data)
                print(f"Alarm triggered for user {alarm.user_id}: Route {route.route_number}")
        
        print(f"Checked {len(active_alarms)} active alarms.")
        
    except Exception as e:
        print(f"Transport alarm check error: {e}")
    finally:
        db.close()


def start_scheduler():
    # Market data - her 5 dakikada bir (1 dakika yerine - daha az yük)
    scheduler.add_job(fetch_market_data, 'interval', minutes=5)
    
    # News ve analysis - her 2 saatte bir (daha az sıklıkla)
    scheduler.add_job(update_news_and_analyze, 'interval', hours=2)
    
    # Transport alarms - her 1 dakikada bir kontrol
    scheduler.add_job(check_transport_alarms, 'interval', minutes=1)
    
    # İlk başlatmada hemen çalıştır (5 saniye sonra)
    scheduler.add_job(fetch_market_data, trigger='date', 
                     run_date=datetime.datetime.now() + datetime.timedelta(seconds=5))
    
    scheduler.add_job(update_news_and_analyze, trigger='date', 
                     run_date=datetime.datetime.now() + datetime.timedelta(seconds=10))
    
    scheduler.start()
    print("Scheduler started with market data (5min), news analysis (2hours), and transport alarms (1min) jobs")


