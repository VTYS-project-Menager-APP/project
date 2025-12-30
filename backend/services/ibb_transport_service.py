"""
Istanbul Metropolitan Municipality (İBB) İETT Bus API Integration Service
Gerçek zamanlı otobüs takip servisi
"""

import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# İBB İETT API Base URLs
IBB_BASE_URL = "https://api.ibb.gov.tr"
IETT_FILO_DURUM_URL = f"{IBB_BASE_URL}/iett/FiloDurum"

class IBBTransportService:
    """İstanbul Büyükşehir Belediyesi otobüs API entegrasyonu"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """HTTP client'ı kapat"""
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """API request headers"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    async def get_sefer_gerceklesme(self, hat_kodu: str) -> Optional[Dict]:
        """
        Belirli bir hat için sefer gerçekleşme bilgilerini getir
        
        Args:
            hat_kodu: Otobüs hat numarası (örn: "34", "500T")
            
        Returns:
            Sefer bilgileri veya None
        """
        try:
            url = f"{IETT_FILO_DURUM_URL}/SeferGerceklesme"
            params = {"hatKodu": hat_kodu}
            
            response = await self.client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Hat {hat_kodu} için sefer bilgileri alındı")
                return data
            else:
                logger.error(f"İBB API hatası: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Sefer gerçekleşme hatası: {e}")
            return None
    
    async def get_hat_duraklar(self, hat_kodu: str, yon: int = 0) -> Optional[List[Dict]]:
        """
        Belirli bir hattın duraklarını getir
        
        Args:
            hat_kodu: Hat numarası
            yon: Yön (0: Gidiş, 1: Dönüş)
            
        Returns:
            Durak listesi
        """
        try:
            url = f"{IBB_BASE_URL}/iett/HatDurakGuzergah"
            params = {
                "hatKodu": hat_kodu,
                "yon": yon
            }
            
            response = await self.client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Hat durakları hatası: {e}")
            return None
    
    async def get_durak_detay(self, durak_kodu: str) -> Optional[Dict]:
        """
        Durak detaylarını getir
        
        Args:
            durak_kodu: Durak numarası
            
        Returns:
            Durak bilgileri
        """
        try:
            url = f"{IBB_BASE_URL}/iett/DurakDetay"
            params = {"durakKodu": durak_kodu}
            
            response = await self.client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Durak detayı hatası: {e}")
            return None
    
    async def get_duraktan_gecen_hatlar(self, durak_kodu: str) -> Optional[List[Dict]]:
        """
        Belirli bir duraktan geçen tüm hatları getir
        
        Args:
            durak_kodu: Durak numarası
            
        Returns:
            Hat listesi
        """
        try:
            url = f"{IBB_BASE_URL}/iett/DuraktanGecenHatlar"
            params = {"durakKodu": durak_kodu}
            
            response = await self.client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Duraktan geçen hatlar hatası: {e}")
            return None
    
    async def get_otobus_konum(self, plaka: str) -> Optional[Dict]:
        """
        Otobüs gerçek zamanlı konum bilgisi
        
        Args:
            plaka: Otobüs plakası
            
        Returns:
            Konum bilgisi (lat, lng, hız vb.)
        """
        try:
            url = f"{IBB_BASE_URL}/iett/OtobusKonum"
            params = {"plaka": plaka}
            
            response = await self.client.get(
                url,
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            logger.error(f"Otobüs konum hatası: {e}")
            return None
    
    async def calculate_smart_alarm_time(
        self,
        hat_kodu: str,
        hedef_varis_saati: str,
        yurume_suresi_dakika: int
    ) -> Optional[Dict]:
        """
        Akıllı alarm zamanı hesapla
        
        Args:
            hat_kodu: Otobüs hat numarası
            hedef_varis_saati: Hedefteki varış saati (HH:MM formatında)
            yurume_suresi_dakika: Durağa yürüme süresi (dakika)
            
        Returns:
            {
                'alarm_time': datetime,  # Alarm çalması gereken zaman
                'bus_departure': datetime,  # Otobüs kalkış zamanı
                'estimated_arrival': datetime,  # Tahmini varış zamanı
                'message': str  # Kullanıcıya gösterilecek mesaj
            }
        """
        try:
            # Sefer bilgilerini al
            sefer_data = await self.get_sefer_gerceklesme(hat_kodu)
            
            if not sefer_data:
                return None
            
            # Hedef varış saatini parse et
            hedef_saat, hedef_dakika = map(int, hedef_varis_saati.split(':'))
            today = datetime.now().date()
            hedef_varis = datetime.combine(today, datetime.min.time().replace(hour=hedef_saat, minute=hedef_dakika))
            
            # Şu anki zaman
            simdi = datetime.now()
            
            # Otobüs yolculuk süresini tahmin et (API'den gelecek)
            # Şimdilik örnek olarak 30 dakika varsayalım
            otobus_yolculuk_suresi = 30
            
            # Gereken otobüs kalkış zamanı
            gereken_kalkis = hedef_varis - timedelta(minutes=otobus_yolculuk_suresi)
            
            # Kullanıcının durağa varması gereken zaman
            durakta_olmasi_gereken = gereken_kalkis - timedelta(minutes=5)  # 5 dakika güvenlik payı
            
            # Alarm zamanı (evden çıkış zamanı)
            alarm_zamani = durakta_olmasi_gereken - timedelta(minutes=yurume_suresi_dakika)
            
            # Şimdi çıkmalı mı kontrolü
            kalan_zaman = alarm_zamani - simdi
            kalan_dakika = int(kalan_zaman.total_seconds() / 60)
            
            if kalan_dakika <= 5:
                mesaj = f"🚨 HEMEN ÇIKMAN GEREK! {hat_kodu} hattına binersen {hedef_varis_saati}'da iş yerindesin!"
            elif kalan_dakika <= 15:
                mesaj = f"⏰ {kalan_dakika} dakika sonra çıkmalısın. {hat_kodu} hattına bineceksin."
            else:
                mesaj = f"✅ {kalan_dakika} dakika sonra çıkman yeterli. {hat_kodu} hattı ile {hedef_varis_saati}'da varırsın."
            
            return {
                'alarm_time': alarm_zamani,
                'bus_departure': gereken_kalkis,
                'estimated_arrival': hedef_varis,
                'walking_time': yurume_suresi_dakika,
                'minutes_until_alarm': kalan_dakika,
                'message': mesaj,
                'should_trigger_now': kalan_dakika <= 5
            }
            
        except Exception as e:
            logger.error(f"Akıllı alarm hesaplama hatası: {e}")
            return None
    
    async def find_routes_between_locations(
        self,
        origin_durak: str,
        destination_durak: str
    ) -> List[str]:
        """
        İki durak arasındaki tüm otobüs hatlarını bul
        
        Args:
            origin_durak: Başlangıç durağı kodu
            destination_durak: Hedef durak kodu
            
        Returns:
            Hat numaraları listesi
        """
        try:
            # Başlangıç durağından geçen hatlar
            origin_hatlar = await self.get_duraktan_gecen_hatlar(origin_durak)
            # Hedef duraktan geçen hatlar
            dest_hatlar = await self.get_duraktan_gecen_hatlar(destination_durak)
            
            if not origin_hatlar or not dest_hatlar:
                return []
            
            # Her iki duraktan da geçen hatları bul
            origin_hat_kodlari = set([h.get('hatKodu') for h in origin_hatlar])
            dest_hat_kodlari = set([h.get('hatKodu') for h in dest_hatlar])
            
            ortak_hatlar = origin_hat_kodlari.intersection(dest_hat_kodlari)
            
            return list(ortak_hatlar)
            
        except Exception as e:
            logger.error(f"Rota bulma hatası: {e}")
            return []

# Global service instance
_ibb_service: Optional[IBBTransportService] = None

def get_ibb_service() -> IBBTransportService:
    """Global IBB service instance'ı döndür"""
    global _ibb_service
    if _ibb_service is None:
        _ibb_service = IBBTransportService()
    return _ibb_service

async def close_ibb_service():
    """Service'i kapat"""
    global _ibb_service
    if _ibb_service:
        await _ibb_service.close()
        _ibb_service = None

