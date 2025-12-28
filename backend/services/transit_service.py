import os
import json
import redis
import datetime
import requests

# Connect to Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

def get_weather_data(location="Istanbul"):
    """
    Fetches real weather data if API key is present, else returns mock.
    """
    if not OPENWEATHER_API_KEY:
        return {"condition": "Rain", "temp": 12, "traffic_load": "High", "source": "Mock"}
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            condition = data["weather"][0]["main"]
            temp = data["main"]["temp"]
            return {"condition": condition, "temp": temp, "traffic_load": "Normal", "source": "API"}
    except Exception as e:
        print(f"Weather API Error: {e}")
        
    return {"condition": "Clear", "temp": 20, "traffic_load": "Normal", "source": "Fallback"}

def get_active_buses():
    """
    Fetches active bus locations from data.ibb.gov.tr wrapper API.
    """
    try:
        url = "https://mekansal.herokuapp.com/api/filo"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # data is a FeatureCollection
            features = data.get("features", [])
            return len(features)
    except Exception as e:
        print(f"Bus API Error: {e}")
    return 0

def recommend_alarm(user_id: int):
    # In future, fetch user specifics from DB:
    # user = db.query(User).get(user_id)
    target_arrival = "08:00"
    base_travel_time = 30 # minutes
    prep_time = 45 # minutes
    
    # Dynamic Data Check
    context = get_weather_data()
    
    # Calculate Travel Time using OSRM
    origin = "Besiktas, Istanbul" # Mock user location
    destination = "Maslak, Istanbul" # Mock user destination
    
    # 1. Geocode Origin and Destination
    def get_coords(location):
        try:
            # User-Agent is required by Nominatim
            headers = {'User-Agent': 'MenagerApp/1.0'}
            url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
            res = requests.get(url, headers=headers)
            if res.status_code == 200 and len(res.json()) > 0:
                data = res.json()[0]
                return float(data['lon']), float(data['lat'])
        except Exception as e:
            print(f"Geocoding Error: {e}")
        return None, None

    lon1, lat1 = get_coords(origin)
    lon2, lat2 = get_coords(destination)
    
    base_travel_time = 30 # Default fallback
    route_source = "Fallback"
    
    if lon1 and lon2:
        try:
            # OSRM Route
            osrm_url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
            res = requests.get(osrm_url)
            if res.status_code == 200:
                routes = res.json().get("routes", [])
                if routes:
                    duration_seconds = routes[0]["duration"]
                    base_travel_time = round(duration_seconds / 60)
                    route_source = "OpenStreetMap (OSRM)"
        except Exception as e:
            print(f"OSRM Error: {e}")

    weather_delay = 0
    reasons = []
    
    # Basit durum eşleştirmesi
    bad_conditions = ["Rain", "Snow", "Thunderstorm", "Drizzle"]
    if context["condition"] in bad_conditions:
        weather_delay += 15
        reasons.append(f"Hava durumu: {context['condition']} (+15dk)")
        
    if context["traffic_load"] == "High":
        weather_delay += 10
        reasons.append("Trafik Yoğun (Simüle Edilmiş) (+10dk)")
        
    total_minutes_needed = base_travel_time + prep_time + weather_delay
    
    # Calculate Wakeup Time
    # Assuming target_arrival is today 08:00
    arrival_dt = datetime.datetime.strptime(target_arrival, "%H:%M")
    wakeup_dt = arrival_dt - datetime.timedelta(minutes=total_minutes_needed)
    recommended_wakeup = wakeup_dt.strftime("%H:%M")
    
    # Check Active Buses
    active_buses = get_active_buses()
    if active_buses > 0:
        reasons.append(f"Toplu Taşıma Aktif: Yolda {active_buses} otobüs var")

    return {
        "target_arrival": target_arrival,
        "recommended_wakeup": recommended_wakeup,
        "total_delay_added": weather_delay,
        "reasons": reasons,
        "context_source": context.get("source", "Unknown"),
        "route_source": route_source,
        "active_buses": active_buses
    }
