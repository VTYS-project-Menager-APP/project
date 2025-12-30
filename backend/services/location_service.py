"""
Location Service
Konum bazlı işlemler ve yakındaki durakları bulma
"""

import httpx
import asyncio
from typing import List, Dict, Optional, Tuple
from math import radians, sin, cos, sqrt, atan2
import logging

logger = logging.getLogger(__name__)


class LocationService:
    """Konum servisleri - geocoding, nearby stops, vb."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        # Nominatim (OpenStreetMap) için User-Agent gerekli
        self.headers = {
            'User-Agent': 'MenagerApp/1.0 (Transport Alarm System)'
        }
    
    async def close(self):
        """HTTP client'ı kapat"""
        await self.client.aclose()
    
    def calculate_distance(
        self, 
        lat1: float, 
        lon1: float, 
        lat2: float, 
        lon2: float
    ) -> float:
        """
        İki koordinat arasındaki mesafeyi hesapla (Haversine formula)
        
        Returns:
            Mesafe (metre cinsinden)
        """
        R = 6371000  # Dünya yarıçapı (metre)
        
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        distance = R * c
        return distance
    
    async def geocode_address(self, address: str, city: str = "Istanbul") -> Optional[Dict]:
        """
        Adres → Koordinat dönüşümü
        
        Args:
            address: Aranacak adres
            city: Şehir (varsayılan: Istanbul)
        
        Returns:
            {
                'lat': float,
                'lon': float,
                'display_name': str
            }
        """
        try:
            query = f"{address}, {city}, Turkey"
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'accept-language': 'tr'
            }
            
            response = await self.client.get(url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    result = data[0]
                    return {
                        'lat': float(result['lat']),
                        'lon': float(result['lon']),
                        'display_name': result['display_name']
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Geocoding hatası: {e}")
            return None
    
    async def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Koordinat → Adres dönüşümü
        
        Returns:
            Adres string'i
        """
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'accept-language': 'tr'
            }
            
            response = await self.client.get(url, params=params, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('display_name', '')
            
            return None
            
        except Exception as e:
            logger.error(f"Reverse geocoding hatası: {e}")
            return None
    
    async def find_nearby_stops_from_ibb(
        self, 
        lat: float, 
        lon: float, 
        radius_meters: int = 500
    ) -> List[Dict]:
        """
        İBB API'sinden yakındaki durakları bul
        
        Not: İBB API'sinde location-based search yoksa,
        tüm durakları alıp manuel filtrelememiz gerekebilir.
        Şimdilik mock data döneceğiz.
        
        Returns:
            [{
                'durak_kodu': str,
                'durak_adi': str,
                'lat': float,
                'lon': float,
                'distance': float (metre)
            }]
        """
        try:
            # TODO: İBB API'si ile implement et
            # Şimdilik İstanbul'un popüler duraklarını hardcode ediyoruz
            
            # İstanbul'daki örnek duraklar (gerçek koordinatlar)
            sample_stops = [
                {'durak_kodu': '104803', 'durak_adi': 'Kadıköy İskele', 'lat': 40.9972, 'lon': 29.0254},
                {'durak_kodu': '100455', 'durak_adi': 'Zincirlikuyu', 'lat': 41.0662, 'lon': 29.0221},
                {'durak_kodu': '102345', 'durak_adi': 'Taksim Meydanı', 'lat': 41.0370, 'lon': 28.9859},
                {'durak_kodu': '103456', 'durak_adi': 'Beşiktaş İskele', 'lat': 41.0422, 'lon': 29.0084},
                {'durak_kodu': '105678', 'durak_adi': 'Mecidiyeköy', 'lat': 41.0627, 'lon': 28.9955},
                {'durak_kodu': '106789', 'durak_adi': 'Şişli', 'lat': 41.0601, 'lon': 28.9869},
                {'durak_kodu': '107890', 'durak_adi': 'Bakırköy', 'lat': 40.9808, 'lon': 28.8736},
                {'durak_kodu': '108901', 'durak_adi': 'Eminönü', 'lat': 41.0174, 'lon': 28.9706},
                {'durak_kodu': '109012', 'durak_adi': 'Üsküdar', 'lat': 41.0255, 'lon': 29.0096},
                {'durak_kodu': '110123', 'durak_adi': 'Levent', 'lat': 41.0778, 'lon': 29.0115},
            ]
            
            # Yakındaki durakları filtrele
            nearby_stops = []
            for stop in sample_stops:
                distance = self.calculate_distance(lat, lon, stop['lat'], stop['lon'])
                if distance <= radius_meters:
                    nearby_stops.append({
                        **stop,
                        'distance': round(distance, 2)
                    })
            
            # Mesafeye göre sırala
            nearby_stops.sort(key=lambda x: x['distance'])
            
            logger.info(f"Konum ({lat}, {lon}) yakınında {len(nearby_stops)} durak bulundu")
            return nearby_stops
            
        except Exception as e:
            logger.error(f"Yakındaki durakları bulma hatası: {e}")
            return []
    
    async def find_routes_between_stops(
        self,
        origin_stop_code: str,
        destination_stop_code: str,
        ibb_service
    ) -> List[Dict]:
        """
        İki durak arasındaki tüm otobüs hatlarını bul
        
        Args:
            origin_stop_code: Başlangıç durak kodu
            destination_stop_code: Hedef durak kodu
            ibb_service: IBBTransportService instance
        
        Returns:
            [{
                'hat_kodu': str,
                'hat_adi': str,
                'estimated_duration': int (dakika)
            }]
        """
        try:
            # Başlangıç durağından geçen hatlar
            origin_routes = await ibb_service.get_duraktan_gecen_hatlar(origin_stop_code)
            # Hedef duraktan geçen hatlar
            dest_routes = await ibb_service.get_duraktan_gecen_hatlar(destination_stop_code)
            
            if not origin_routes or not dest_routes:
                # API çalışmıyorsa mock data
                return self._get_mock_routes_for_stops(origin_stop_code, destination_stop_code)
            
            # Her iki duraktan da geçen hatları bul
            origin_codes = set([r.get('hatKodu') for r in origin_routes if r.get('hatKodu')])
            dest_codes = set([r.get('hatKodu') for r in dest_routes if r.get('hatKodu')])
            
            common_routes = origin_codes.intersection(dest_codes)
            
            routes = []
            for code in common_routes:
                routes.append({
                    'hat_kodu': code,
                    'hat_adi': code,  # İBB API'den gelirse daha detaylı olur
                    'estimated_duration': 30  # Varsayılan 30 dakika
                })
            
            return routes
            
        except Exception as e:
            logger.error(f"Hat arama hatası: {e}")
            return self._get_mock_routes_for_stops(origin_stop_code, destination_stop_code)
    
    def _get_mock_routes_for_stops(
        self, 
        origin_code: str, 
        dest_code: str
    ) -> List[Dict]:
        """Mock data - Gerçek API çalışmadığında"""
        
        # Popüler hatlar ve gittikleri yerler (basitleştirilmiş)
        route_mapping = {
            ('104803', '100455'): ['34', '34A', '34AS', '34G'],  # Kadıköy -> Zincirlikuyu
            ('104803', '102345'): ['110', '112', '14', '15'],     # Kadıköy -> Taksim
            ('102345', '100455'): ['30D', '42T', 'DT1'],         # Taksim -> Zincirlikuyu
            ('103456', '110123'): ['40', '40T', '42T'],          # Beşiktaş -> Levent
            ('108901', '109012'): ['15F', '15P', '15'],          # Eminönü -> Üsküdar
        }
        
        # Direkt eşleşme var mı?
        key = (origin_code, dest_code)
        if key in route_mapping:
            return [
                {
                    'hat_kodu': code,
                    'hat_adi': code,
                    'estimated_duration': 30
                }
                for code in route_mapping[key]
            ]
        
        # Ters yön kontrol et
        reverse_key = (dest_code, origin_code)
        if reverse_key in route_mapping:
            return [
                {
                    'hat_kodu': code,
                    'hat_adi': f"{code} (Ters Yön)",
                    'estimated_duration': 30
                }
                for code in route_mapping[reverse_key]
            ]
        
        # Hiç eşleşme yoksa genel hatlar döndür
        return [
            {'hat_kodu': '34', 'hat_adi': '34', 'estimated_duration': 35},
            {'hat_kodu': '500T', 'hat_adi': '500T', 'estimated_duration': 40},
        ]
    
    async def find_all_routes_near_locations(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        ibb_service,
        radius_meters: int = 500
    ) -> Dict:
        """
        İki konum yakınındaki tüm durakları bul ve
        bu duraklar arasındaki tüm otobüs hatlarını listele
        
        Returns:
            {
                'origin_stops': [...],
                'destination_stops': [...],
                'all_routes': [...],
                'route_count': int
            }
        """
        try:
            # Her iki konum için de yakındaki durakları bul
            origin_stops = await self.find_nearby_stops_from_ibb(
                origin_lat, origin_lon, radius_meters
            )
            dest_stops = await self.find_nearby_stops_from_ibb(
                dest_lat, dest_lon, radius_meters
            )
            
            if not origin_stops or not dest_stops:
                logger.warning("Bir veya iki konumda durak bulunamadı")
                return {
                    'origin_stops': origin_stops,
                    'destination_stops': dest_stops,
                    'all_routes': [],
                    'route_count': 0
                }
            
            # Tüm durak kombinasyonları için hatları bul
            all_routes_dict = {}  # hat_kodu: route_info
            
            # Transfer/Dolaylı hatlar için sadece başlangıçtan geçenler
            origin_only_routes_dict = {}

            for origin_stop in origin_stops[:3]:  # İlk 3 durak yeterli
                # Başlangıç durağından geçen hatları al (Transfer önerisi için)
                if ibb_service:
                    try:
                        stop_routes = await ibb_service.get_duraktan_gecen_hatlar(origin_stop['durak_kodu'])
                        if stop_routes:
                            for r in stop_routes:
                                if r.get('hatKodu') and r.get('hatKodu') not in origin_only_routes_dict:
                                    origin_only_routes_dict[r.get('hatKodu')] = {
                                        'hat_kodu': r.get('hatKodu'),
                                        'hat_adi': r.get('hatAdi') or r.get('hatKodu'),
                                        'origin_stop': origin_stop['durak_adi'],
                                        'estimated_duration': 45 # Tahmini
                                    }
                    except:
                        pass

                for dest_stop in dest_stops[:3]:
                    routes = await self.find_routes_between_stops(
                        origin_stop['durak_kodu'],
                        dest_stop['durak_kodu'],
                        ibb_service
                    )
                    
                    for route in routes:
                        if route['hat_kodu'] not in all_routes_dict:
                            all_routes_dict[route['hat_kodu']] = {
                                **route,
                                'origin_stop': origin_stop['durak_adi'],
                                'dest_stop': dest_stop['durak_adi']
                            }
            
            all_routes = list(all_routes_dict.values())
            origin_only_routes = list(origin_only_routes_dict.values())
            
            return {
                'origin_stops': origin_stops,
                'destination_stops': dest_stops,
                'all_routes': all_routes,
                'origin_only_routes': origin_only_routes,
                'route_count': len(all_routes)
            }
            
        except Exception as e:
            logger.error(f"Konum bazlı hat bulma hatası: {e}")
            return {
                'origin_stops': [],
                'destination_stops': [],
                'all_routes': [],
                'route_count': 0
            }


# Global service instance
_location_service: Optional[LocationService] = None

def get_location_service() -> LocationService:
    """Global location service instance"""
    global _location_service
    if _location_service is None:
        _location_service = LocationService()
    return _location_service

async def close_location_service():
    """Service'i kapat"""
    global _location_service
    if _location_service:
        await _location_service.close()
        _location_service = None

