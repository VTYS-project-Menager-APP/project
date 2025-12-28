"""
Prediction Service - Olay bazlı piyasa etkisi tahmini
Basit korelasyon analizi kullanır
"""

from database import SessionLocal
from models import HistoricalEvent, MarketEventCorrelation, CurrentEvent
from sqlalchemy import func
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionService:
    
    def __init__(self):
        self.db = SessionLocal()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        İki metin arasında basit benzerlik hesaplar (kelime bazlı)
        Daha gelişmiş NLP için TF-IDF veya word embeddings kullanılabilir
        """
        if not text1 or not text2:
            return 0.0
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def find_similar_events(self, current_event: CurrentEvent, limit=5) -> List[Dict]:
        """
        Geçmiş olaylar arasından en benzerlerini bulur
        """
        try:
            historical_events = self.db.query(HistoricalEvent).all()
            
            similarities = []
            for hist_event in historical_events:
                # Başlık ve kategori benzerliği
                title_sim = self.calculate_similarity(current_event.title, hist_event.title)
                
                # Kategori eşleşmesi bonusu
                category_bonus = 0.3 if current_event.category == hist_event.category else 0.0
                
                total_similarity = title_sim + category_bonus
                
                if total_similarity > 0.1:  # Minimum benzerlik eşiği
                    similarities.append({
                        'event': hist_event,
                        'similarity': total_similarity
                    })
            
            # En yüksek benzerlik skoruna göre sırala
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Benzer olay arama hatası: {str(e)}")
            return []
    
    def predict_impact(self, current_event: CurrentEvent, symbol='GOLD') -> Dict:
        """
        Bir olayın belirli bir piyasa üzerindeki etkisini tahmin eder
        """
        try:
            # Benzer geçmiş olayları bul
            similar_events = self.find_similar_events(current_event, limit=10)
            
            if not similar_events:
                return {
                    'predicted_impact': 0.0,
                    'confidence': 0.0,
                    'direction': 'neutral',
                    'similar_events_count': 0,
                    'message': 'Benzer geçmiş olay bulunamadı'
                }
            
            # Bu olayların piyasa etkilerini topla
            total_percent_change = 0.0
            positive_count = 0
            negative_count = 0
            correlations_found = 0
            
            for item in similar_events:
                event = item['event']
                similarity = item['similarity']
                
                # Bu olayın market korelasyonlarını bul
                correlations = self.db.query(MarketEventCorrelation).filter(
                    MarketEventCorrelation.event_id == event.id,
                    MarketEventCorrelation.symbol == symbol
                ).all()
                
                for corr in correlations:
                    # Benzerlik ağırlıklı değişim
                    weighted_change = corr.percent_change * similarity
                    total_percent_change += weighted_change
                    correlations_found += 1
                    
                    if corr.percent_change > 0:
                        positive_count += 1
                    elif corr.percent_change < 0:
                        negative_count += 1
            
            if correlations_found == 0:
                return {
                    'predicted_impact': 0.0,
                    'confidence': 0.0,
                    'direction': 'neutral',
                    'similar_events_count': len(similar_events),
                    'message': 'Benzer olaylar bulundu ancak piyasa verisi yok'
                }
            
            # Ortalama değişim
            avg_percent_change = total_percent_change / correlations_found
            
            # Yön belirleme
            if positive_count > negative_count:
                direction = 'positive'
            elif negative_count > positive_count:
                direction = 'negative'
            else:
                direction = 'neutral'
            
            # Güven skoru (benzer olay sayısı ve korelasyon gücüne göre)
            confidence = min(1.0, correlations_found / 10.0)
            
            # Tahmin edilen etki skoru (0-10 arası)
            impact_score = abs(avg_percent_change) / 2.0  # Yüzde değişimi skora çevir
            impact_score = min(10.0, max(0.0, impact_score))
            
            return {
                'predicted_impact': round(impact_score, 2),
                'confidence': round(confidence, 2),
                'direction': direction,
                'avg_percent_change': round(avg_percent_change, 2),
                'similar_events_count': len(similar_events),
                'correlations_found': correlations_found,
                'message': f"{len(similar_events)} benzer olay, {correlations_found} piyasa korelasyonu bulundu"
            }
            
        except Exception as e:
            logger.error(f"Tahmin hesaplama hatası: {str(e)}")
            return {
                'predicted_impact': 0.0,
                'confidence': 0.0,
                'direction': 'neutral',
                'error': str(e)
            }
    
    def analyze_all_pending_events(self):
        """
        Henüz analiz edilmemiş tüm güncel olayları analiz eder
        """
        try:
            pending_events = self.db.query(CurrentEvent).filter(
                CurrentEvent.analyzed == 0
            ).all()
            
            analyzed_count = 0
            
            for event in pending_events:
                # Her iki piyasa için tahmin yap
                symbols = ['GOLD', 'USDTRY']
                
                max_impact = 0.0
                for symbol in symbols:
                    prediction = self.predict_impact(event, symbol)
                    if prediction['predicted_impact'] > max_impact:
                        max_impact = prediction['predicted_impact']
                
                # En yüksek etkiyi kaydet
                event.predicted_impact = max_impact
                event.analyzed = 1
                analyzed_count += 1
            
            self.db.commit()
            logger.info(f"{analyzed_count} olay analiz edildi.")
            
            return analyzed_count
            
        except Exception as e:
            logger.error(f"Toplu analiz hatası: {str(e)}")
            self.db.rollback()
            return 0
    
    def get_top_impact_events(self, limit=5) -> List[CurrentEvent]:
        """
        En yüksek etkili güncel olayları döndürür
        """
        try:
            events = self.db.query(CurrentEvent).filter(
                CurrentEvent.analyzed == 1
            ).order_by(
                CurrentEvent.predicted_impact.desc()
            ).limit(limit).all()
            
            return events
            
        except Exception as e:
            logger.error(f"Top events sorgusu hatası: {str(e)}")
            return []
    
    def generate_narrative(self, event_title, percent_change, symbol='GOLD') -> str:
        """
        Geçmiş verilere dayanarak anlamlı bir özet/tavsiye üretir
        """
        direction = "yükseliş" if percent_change > 0 else "düşüş"
        change_abs = abs(percent_change)
        
        market_name = "Altın" if symbol == "GOLD" else "Dolar/TL"
        
        # Basit kural tabanlı anlatım
        narrative = f"{event_title} sonrasında geçmişte {market_name} piyasasında %{change_abs:.2f} oranında bir {direction} yaşandı."
        
        if change_abs > 3:
            narrative += f" Bu olay kritik bir etkiye sahip olmuştu, benzer bir durumda sert bir hareket beklenebilir."
        elif change_abs > 1:
            narrative += f" Bu olayla bağlantılı olarak genel bir {direction} eğilimi gözlemlenebilir."
        else:
            narrative += f" Etkisi sınırlı kalsa da piyasa yönü açısından takip edilmelidir."
            
        return narrative

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()


# Global instance
prediction_service = PredictionService()


if __name__ == "__main__":
    # Test
    service = PredictionService()
    count = service.analyze_all_pending_events()
    print(f"{count} olay analiz edildi")
    
    top_events = service.get_top_impact_events(5)
    for event in top_events:
        print(f"{event.title}: Impact={event.predicted_impact}")
