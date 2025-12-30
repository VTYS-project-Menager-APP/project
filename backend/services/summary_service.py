import json
import logging
import datetime
import requests
from database import SessionLocal
from models import MarketSummary, CurrentMarketRate, CurrentEvent, UpcomingEvent, HistoricalEvent, MarketEventCorrelation
from services.prediction_service import prediction_service
from services.trading_economics_service import trading_economics_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SummaryService:
    def __init__(self):
        import os
        # Docker network içinde 'ollama' servis adını kullan, fallback olarak localhost
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")
        self.model = "llama3" # Kullanıcı makinesinde hangi model varsa, varsayılan llama3
        logger.info(f"Ollama URL configured: {self.ollama_url}")

    def _call_ollama(self, prompt):
        """Ollama API'sine istek atar."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            # LLM detaylı analiz için daha fazla zamana ihtiyaç duyabilir
            response = requests.post(self.ollama_url, json=payload, timeout=180)
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                logger.error(f"Ollama error: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            return None

    def generate_hourly_summary(self):
        """
        Her saat başı piyasa verilerini, haberleri ve gelecek olayları birleştirerek 
        Ollama (LLM) destekli özet oluşturur.
        """
        db = SessionLocal()
        try:
            # 1. Güncel kurları al
            rates = db.query(CurrentMarketRate).all()
            rates_list = []
            for r in rates:
                rates_list.append({
                    "symbol": r.symbol,
                    "name": r.name,
                    "price": r.price,
                    "change": r.daily_change_percent
                })

            # 2. En yüksek etkili güncel haberleri al ve detaylı analiz yap
            top_news = db.query(CurrentEvent).filter(CurrentEvent.analyzed == 1).order_by(CurrentEvent.predicted_impact.desc()).limit(3).all()
            
            # Haberler için geçmiş benzerlikleri bul ve detaylı analiz yap
            news_context = []
            news_snapshot = []
            detailed_correlations = []
            
            for news in top_news:
                similar_events = prediction_service.find_similar_events(news, limit=3)  # Daha fazla benzer olay
                
                if similar_events:
                    # Her benzer olay için korelasyonları topla
                    event_analysis = {
                        'current_title': news.title,
                        'historical_matches': []
                    }
                    
                    for sim_item in similar_events:
                        hist_event = sim_item['event']
                        similarity_score = sim_item['similarity']
                        
                        # Korelasyonları detaylı al
                        correlations = db.query(MarketEventCorrelation).filter(
                            MarketEventCorrelation.event_id == hist_event.id
                        ).all()
                        
                        if correlations:
                            for corr in correlations:
                                event_analysis['historical_matches'].append({
                                    'date': hist_event.event_date.strftime('%d.%m.%Y'),
                                    'title': hist_event.title,
                                    'similarity': round(similarity_score * 100, 1),
                                    'symbol': corr.symbol,
                                    'price_before': corr.price_before,
                                    'price_after': corr.price_after,
                                    'percent_change': corr.percent_change,
                                    'days_after': corr.days_after,
                                    'correlation_strength': corr.correlation_strength
                                })
                    
                    if event_analysis['historical_matches']:
                        detailed_correlations.append(event_analysis)
                        
                        # Ortalama değişim hesapla
                        gold_changes = [m['percent_change'] for m in event_analysis['historical_matches'] if m['symbol'] == 'GOLD']
                        usd_changes = [m['percent_change'] for m in event_analysis['historical_matches'] if m['symbol'] == 'USDTRY']
                        
                        avg_gold = sum(gold_changes) / len(gold_changes) if gold_changes else 0
                        avg_usd = sum(usd_changes) / len(usd_changes) if usd_changes else 0
                        
                        context_text = f"- GÜNCEL: {news.title}\n"
                        context_text += f"  GEÇMIŞ ANALİZ: {len(event_analysis['historical_matches'])} benzer olay bulundu.\n"
                        
                        if gold_changes:
                            context_text += f"  ALTIN: Ortalama %{avg_gold:.2f} değişim (Örnekler: "
                            context_text += ", ".join([f"{m['date']} -> %{m['percent_change']:.1f}" for m in event_analysis['historical_matches'][:3] if m['symbol'] == 'GOLD'])
                            context_text += ")\n"
                        
                        if usd_changes:
                            context_text += f"  DOLAR: Ortalama %{avg_usd:.2f} değişim (Örnekler: "
                            context_text += ", ".join([f"{m['date']} -> %{m['percent_change']:.1f}" for m in event_analysis['historical_matches'][:3] if m['symbol'] == 'USDTRY'])
                            context_text += ")\n"
                        
                        news_context.append(context_text)
                
                news_snapshot.append({"title": news.title, "impact": news.predicted_impact, "category": news.category})

            # 3. Yaklaşan önemli olayları al
            upcoming = db.query(UpcomingEvent).order_by(UpcomingEvent.event_date.asc()).limit(3).all()
            upcoming_list = [{"title": u.title, "date": u.event_date.isoformat(), "impact": u.impact_prediction} for u in upcoming]
            upcoming_context = [f"- {u.title} (Tarih: {u.event_date.strftime('%d.%m.%Y')})" for u in upcoming]

            # 4. Prompt Hazırla
            prompt = self._build_ollama_prompt(rates_list, news_context, upcoming_context)
            
            # 5. Ollama'dan Yanıt Al
            llm_response = self._call_ollama(prompt)
            
            summary_text = ""
            advice_text = ""
            
            if llm_response:
                # Basit bir parsing
                # LLM bazen formatı tam tutturamayabilir, basit split deneyelim
                if "TAVSİYE:" in llm_response:
                    parts = llm_response.split("TAVSİYE:")
                    summary_text = parts[0].replace("ÖZET:", "").strip()
                    advice_text = parts[1].strip()
                else:
                    # Başlıkları bulamazsa hepsini özete at
                    summary_text = llm_response
                    advice_text = "Detaylı analiz için piyasa takibine devam ediniz."
            else:
                # Fallback: Eski yöntem
                summary_text = self._build_summary_text_fallback(rates_list, news_snapshot, upcoming_list)
                advice_text = self._build_advice_text_fallback(rates_list, news_snapshot)

            sentiment = self._calculate_overall_sentiment(rates_list, news_snapshot)

            # 6. Kaydet
            new_summary = MarketSummary(
                summary_text=summary_text,
                market_snapshot=json.dumps(rates_list),
                news_snapshot=json.dumps(news_snapshot),
                upcoming_events_snapshot=json.dumps(upcoming_list),
                advice_text=advice_text,
                overall_sentiment=sentiment,
                created_at=datetime.datetime.utcnow()
            )
            db.add(new_summary)
            db.commit()
            logger.info("Hourly market summary generated successfully via AI.")
            return new_summary

        except Exception as e:
            logger.error(f"Error generating hourly summary: {e}")
            db.rollback()
        finally:
            db.close()

    def _build_ollama_prompt(self, rates, news_context, upcoming_context):
        rates_str = "\n".join([f"- {r['name']}: {r['price']} (Günlük Değişim: %{r['change']:.2f})" for r in rates])
        news_str = "\n".join(news_context) if news_context else "Önemli bir haber yok."
        upcoming_str = "\n".join(upcoming_context) if upcoming_context else "Yakında önemli bir olay yok."
        
        return f"""
Sen uzman bir finansal analistsin ve 8000+ tarihsel olay verisine dayanarak piyasa tahminleri yapıyorsun.

=== GÜNCEL PİYASA DURUM ===
{rates_str}

=== TARİHSEL KORELASYON ANALİZİ ===
Aşağıda güncel olaylara benzer geçmiş olaylar ve o zamanki fiyat hareketleri gösteriliyor:

{news_str}

=== YAKLAŞAN OLAYLAR ===
{upcoming_str}

=== GÖREV ===
Yukarıdaki tarihsel verileri kullanarak DETAYLI bir analiz yap:

ÖZET:
[Buraya piyasanın genel durumunu anlatan 2-3 cümlelik özet yaz.]

TAVSİYE:
[ÖNEMLİ: Geçmiş olaylardaki GERÇEK fiyat değişimlerini kullanarak somut tahmin yap.
Örnek format: "2022'de benzer enflasyon açıklamasında altın %2.5 yükseldi, 2020'de %1.8 düştü. Ortalama %1.15 yükseliş göz önüne alındığında, bu sefer de ______ bekleniyor."

Mutlaka şu bilgileri ekle:
1. Kaç tane benzer geçmiş olay var
2. O olaylardaki ortalama fiyat değişimi
3. En yakın benzer olayın tarihi ve sonucu
4. Güncel piyasa koşullarıyla karşılaştırma
5. Kısa vadeli (1 hafta) ve orta vadeli (1 ay) somut fiyat beklentisi

4-5 cümlelik detaylı analiz yaz.]
"""

    def _build_summary_text_fallback(self, rates, news, upcoming):
        """Metin tabanlı özet oluşturur (Yedek)."""
        text = "Piyasa şu anda "
        usd = next((r for r in rates if r['symbol'] == 'USDTRY'), None)
        gold = next((r for r in rates if r['symbol'] == 'GOLD'), None)
        
        if usd and gold:
            usd_dir = "yükseliş" if usd['change'] > 0 else "düşüş"
            gold_dir = "yükseliş" if gold['change'] > 0 else "düşüş"
            text += f"Dolar/TL tarafında %{abs(usd['change']):.2f} {usd_dir}, Altın tarafında ise %{abs(gold['change']):.2f} {gold_dir} eğilimiyle işlem görüyor. "
        
        return text

    def _build_advice_text_fallback(self, rates, news):
        """Kullanıcıya yönelik tavsiye metni (Yedek)."""
        gold = next((r for r in rates if r['symbol'] == 'GOLD'), None)
        advice = "Genel piyasa dinamikleri göz önüne alındığında; "
        if gold and gold['change'] < -0.5:
            advice += "Altın fiyatlarındaki geri çekilme, orta vadeli yatırımcılar için alım fırsatı olabilir. "
        else:
            advice += "Piyasalar veri odaklı yatay bir seyir izliyor."
        return advice

    def _calculate_overall_sentiment(self, rates, news):
        """Genel piyasa duyarlılığını hesaplar."""
        score = 0
        for r in rates:
            if r['change'] > 0.2: score += 1
            if r['change'] < -0.2: score -= 1
        
        if score > 0: return "Positive"
        if score < 0: return "Negative"
        return "Neutral"

summary_service = SummaryService()
