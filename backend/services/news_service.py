"""
NewsAPI Service - Güncel ekonomi ve finans haberlerini çeker
"""

from newsapi import NewsApiClient
from database import SessionLocal
from models import CurrentEvent
import datetime
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsService:
    def __init__(self):
        api_key = os.getenv("NEWS_API_KEY", "")
        if not api_key:
            logger.warning("NEWS_API_KEY bulunamadı!")
        self.newsapi = NewsApiClient(api_key=api_key) if api_key else None
    
    def fetch_current_news(self, language='en', page_size=20):
        """
        Güncel ekonomi ve finans haberlerini çeker
        """
        if not self.newsapi:
            logger.error("NewsAPI client başlatılamadı!")
            return []
        
        try:
            # Türkçe ekonomi haberleri
            response = self.newsapi.get_top_headlines(
                category='business',
                language=language,
                page_size=page_size
            )
            
            if response.get('status') == 'ok':
                articles = response.get('articles', [])
                logger.info(f"{len(articles)} haber çekildi.")
                return articles
            else:
                logger.error(f"NewsAPI hatası: {response.get('message', 'Bilinmeyen hata')}")
                # Fallback to sample news if API key is invalid
                if "apiKeyInvalid" in response.get('code', ''):
                    return get_sample_news()
                return []
                
        except Exception as e:
            logger.error(f"Haber çekme hatası: {str(e)}")
            return get_sample_news()
    
    def fetch_specific_keywords(self, keywords=['altın', 'dolar', 'kur', 'merkez bankası', 'enflasyon']):
        """
        Belirli anahtar kelimelerle haber arar
        """
        if not self.newsapi:
            return []
        
        try:
            query = ' OR '.join(keywords)
            from_date = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime('%Y-%m-%d')
            response = self.newsapi.get_everything(
                q=query,
                language='en',
                sort_by='publishedAt',
                page_size=20,
                from_param=from_date
            )
            
            if response.get('status') == 'ok':
                articles = response.get('articles', [])
                logger.info(f"{len(articles)} anahtar kelime bazlı haber bulundu.")
                return articles
            else:
                if "apiKeyInvalid" in response.get('code', ''):
                    return get_sample_news()
                return []
                
        except Exception as e:
            logger.error(f"Anahtar kelime arama hatası: {str(e)}")
            return get_sample_news()
    
    def store_news_to_db(self, articles):
        """
        Haberleri database'e kaydeder
        """
        db = SessionLocal()
        stored_count = 0
        
        try:
            for article in articles:
                # Aynı URL varsa ekleme
                existing = db.query(CurrentEvent).filter_by(url=article.get('url')).first()
                if existing:
                    continue
                
                # Kategoriyi belirle
                category = self.categorize_news(article)
                
                event = CurrentEvent(
                    title=article.get('title', 'No Title')[:500],  # String limiti
                    description=article.get('description', '')[:1000] if article.get('description') else '',
                    published_at=self.parse_published_date(article.get('publishedAt')),
                    category=category,
                    source='newsapi',
                    url=article.get('url', ''),
                    predicted_impact=0.0,  # Henüz analiz edilmedi
                    analyzed=0
                )
                
                db.add(event)
                stored_count += 1
            
            db.commit()
            logger.info(f"{stored_count} yeni haber database'e eklendi.")
            
        except Exception as e:
            logger.error(f"Database kayıt hatası: {str(e)}")
            db.rollback()
        finally:
            db.close()
        
        return stored_count
    
    def categorize_news(self, article):
        """
        Haberin kategorisini belirler
        """
        title = article.get('title', '').lower()
        description = article.get('description', '').lower() if article.get('description') else ''
        
        text = f"{title} {description}"
        
        if any(word in text for word in ['altın', 'gold', 'ons']):
            return 'altın'
        elif any(word in text for word in ['dolar', 'dollar', 'kur', 'döviz', 'usd']):
            return 'döviz'
        elif any(word in text for word in ['merkez bankası', 'fed', 'faiz', 'enflasyon']):
            return 'para_politikası'
        elif any(word in text for word in ['borsa', 'hisse', 'bist']):
            return 'borsa'
        else:
            return 'genel_ekonomi'
    
    def parse_published_date(self, date_str):
        """
        Tarih string'ini datetime'a çevirir
        """
        try:
            if date_str:
                # ISO format: 2023-12-31T10:30:00Z
                return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return datetime.datetime.now()
        except:
            return datetime.datetime.now()
    
    def update_all_news(self):
        """
        Tüm haberleri günceller (scheduler için)
        """
        logger.info("Haber güncelleme başlatılıyor...")
        
        # Top headlines
        top_articles = self.fetch_current_news()
        stored1 = self.store_news_to_db(top_articles)
        
        # Keyword search
        keyword_articles = self.fetch_specific_keywords()
        stored2 = self.store_news_to_db(keyword_articles)
        
        total = stored1 + stored2
        logger.info(f"Toplam {total} yeni haber eklendi.")
        return total


def get_sample_news():
    """
    API key yoksa örnek haberler döndür
    """
    return [
        {
            "title": "Altın Fiyatları Yükselişe Geçti",
            "description": "Küresel piyasalarda altın ons fiyatı son 1 ayın zirvesine ulaştı.",
            "publishedAt": datetime.datetime.now().isoformat(),
            "url": "https://example.com/news1"
        },
        {
            "title": "Dolar/TL Kurunda Volatilite",
            "description": "Merkez Bankası açıklamasının ardından dolar/TL kurunda dalgalanma yaşandı.",
            "publishedAt": datetime.datetime.now().isoformat(),
            "url": "https://example.com/news2"
        }
    ]


# Global instance
news_service = NewsService()


if __name__ == "__main__":
    # Test
    service = NewsService()
    service.update_all_news()
