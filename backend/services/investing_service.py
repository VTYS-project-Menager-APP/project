import cloudscraper
from bs4 import BeautifulSoup
import datetime
import logging
from database import SessionLocal
from models import UpcomingEvent
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InvestingService:
    def __init__(self):
        self.url = "https://www.investing.com/economic-calendar/"
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

    def scrape_calendar(self):
        """
        Scrapes the official Investing.com economic calendar.
        """
        try:
            response = self.scraper.get(self.url, timeout=15)
            if response.status_code != 200:
                logger.error(f"Failed to fetch Investing.com: Status {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'economicCalendarData'})
            if not table:
                logger.error("Could not find economicCalendarData table")
                return []

            all_rows = table.find_all('tr')
            current_date = datetime.datetime.now()
            
            for row in all_rows:
                # Meta verileri içeren satırları atla
                if 'class' in row.attrs and 'js-event-item' not in row['class'] and 'id' not in row.attrs:
                    continue
                
                # Tarih başlığı satırını kontrol et
                if 'id' in row.attrs and row.attrs['id'].startswith('theDay'):
                    try:
                        # id Genellikle 'theDay2024-12-29' formatındadır
                        date_str = row.attrs['id'].replace('theDay', '')
                        current_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        pass
                    continue
                
                # Etkinlik satırını kontrol et
                if 'class' in row.attrs and 'js-event-item' in row['class']:
                    try:
                        cells = row.find_all('td')
                        if len(cells) < 7: continue
                        
                        time_val = cells[0].get_text(strip=True)
                        currency = cells[1].get_text(strip=True)
                        
                        # Önem (boğa kafaları)
                        importance_td = cells[2]
                        # 'left' class'lı i elementleri boğaları temsil eder
                        bulls = importance_td.find_all('i', class_=re.compile(r'bullish\d'))
                        if not bulls:
                            # Yedek metod: i elementlerinin sayısına bak
                            bulls = importance_td.find_all('i', class_='grayFullBullishIcon')
                            
                        # Investing bazen i'leri i.grayFullBullishIcon olarak saklar
                        importance_level = len(bulls)
                        
                        # Alternatif önem tespiti (bazen class ismi 'left grayFullBullishIcon' olur)
                        if importance_level == 0:
                            importance_level = len(importance_td.find_all('i', class_='left'))
                        
                        event_name = cells[3].get_text(strip=True)
                        actual = cells[4].get_text(strip=True)
                        forecast = cells[5].get_text(strip=True)
                        previous = cells[6].get_text(strip=True)
                        
                        # Sadece orta ve yüksek önemdekileri al (veya USD/TRY ise hepsini)
                        if importance_level < 2 and currency not in ['USD', 'TRY']:
                            continue
                            
                        if currency not in ['USD', 'TRY', 'EUR', 'GBP']:
                            continue

                        events.append({
                            'time': time_val,
                            'currency': currency,
                            'importance': importance_level,
                            'event': event_name,
                            'actual': actual,
                            'forecast': forecast,
                            'previous': previous,
                            'date': current_date
                        })
                    except Exception as e:
                        logger.warning(f"Row parsing error: {e}")
                        continue
            
            return events
            
        except Exception as e:
            logger.error(f"Error scraping Investing.com: {e}")
            return []

    def update_upcoming_events(self):
        """
        Scrapes and updates the UpcomingEvent table in DB.
        """
        events = self.scrape_calendar()
        if not events:
            return 0
        
        db = SessionLocal()
        added_count = 0
        
        try:
            # Sadece gelecekteki olayları koruyalım veya temizleyip yeniden ekleyelim
            # Şimdilik: Mevcut ekonomik takvim verilerini temizleyip günceli eklemek daha tutarlı
            db.query(UpcomingEvent).filter(UpcomingEvent.category == "ekonomik_takvim").delete()
            
            for ev in events:
                title = f"[{ev['currency']}] {ev['event']}"
                
                # Create description
                desc = f"Önem Derecesi: {ev['importance']}/3. Beklenen: {ev['forecast'] or '-'}, Önceki: {ev['previous'] or '-'}"
                if ev.get('actual'):
                    desc += f", Gerçekleşen: {ev['actual']}"
                
                # Determine impact prediction
                impact = "Orta Etki Beklentisi"
                if ev['importance'] == 3:
                    impact = "Yüksek Volatilite Beklentisi"
                
                # Advice
                advice = self.generate_simple_advice(ev)
                
                new_event = UpcomingEvent(
                    title=title,
                    description=desc,
                    event_date=ev['date'],
                    category="ekonomik_takvim",
                    impact_prediction=impact,
                    ai_advice=advice
                )
                db.add(new_event)
                added_count += 1
            
            db.commit()
            return added_count
        except Exception as e:
            logger.error(f"Error updating DB: {e}")
            db.rollback()
            return 0
        finally:
            db.close()

    def generate_simple_advice(self, event):
        """
        Generates a rule-based advice for the event.
        """
        name = event['event'].lower()
        currency = event['currency']
        
        if 'interest rate' in name or 'faiz' in name:
            return f"{currency} bölgesindeki bu faiz kararı piyasalar için en kritik veridir. Tahminin üzerinde bir rakam {currency} paritesini güçlendirir, altını baskılar."
        
        if 'cpi' in name or 'enflasyon' in name:
            return f"Enflasyon verisi {currency} faiz beklentilerini doğrudan etkiler. Yüksek enflasyon genellikle şahin bir merkez bankası ve güçlü bir para birimi beklentisi yaratır."
        
        if 'payroll' in name or 'istihdam' in name:
            return "İstihdam verileri ekonomik canlılığı gösterir. Güçlü veriler dolar endeksini (DXY) yukarı taşıyarak altın üzerinde satış baskısı kurabilir."
            
        return f"Bu ekonomik gösterge {currency} bazlı varlıklarda kısa süreli volatilite yaratabilir. Geçmişteki benzer veriler sonrası %0.5 ile %1.5 arasında dalgalanmalar görülmüştür."

investing_service = InvestingService()
