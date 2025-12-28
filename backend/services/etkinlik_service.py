
import httpx
import os
from typing import List, Dict, Any

ETKINLIK_API_URL = "https://backend.etkinlik.io/api/v2"
API_TOKEN = os.getenv("ETKINLIK_API_TOKEN")

async def get_events(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches events from Etkinlik.io API.
    """
    if not API_TOKEN:
        print("Warning: ETKINLIK_API_TOKEN is not set.")
        return []

    headers = {
        "X-Etkinlik-Token": API_TOKEN
    }
    
    # Example endpoint: /events
    # Documentation says /events or similar from analysis
    # We used 'https://backend.etkinlik.io/api/v2/events' successfully in curl
    
    url = f"{ETKINLIK_API_URL}/events"
    params = {
        "take": limit, 
        "skip": 0
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            # The structure depends on API response, usually 'items' or direct list
            # Based on common practices and curl check earlier (though I didn't see deep output)
            return data.get('items', []) if isinstance(data, dict) else data
        except httpx.HTTPError as e:
            print(f"Error fetching events from Etkinlik.io: {e}")
            return []
