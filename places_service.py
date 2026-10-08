import aiohttp
import math
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv(override=True)
GEOAPIFY_KEY = os.getenv("GEOAPIFY_API_KEY")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R*2*math.atan2(math.sqrt(a), math.sqrt(1-a))

async def search_nearby(lat: float, lon: float, radius_m: int = 1000, category: str = "restaurant") -> Dict[str, Any]:
    # Geoapify categories: catering.restaurant, catering.fast_food, catering.cafe
    url = "https://api.geoapify.com/v2/places"
    params = {
        "categories": "catering.restaurant,catering.fast_food,catering.cafe",
        "filter": f"circle:{lon},{lat},{radius_m}",
        "bias": f"proximity:{lon},{lat}",
        "limit": 20,
        "apiKey": GEOAPIFY_KEY
    }
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params, timeout=15) as r:
            r.raise_for_status()
            data = await r.json()
            restaurants = []
            for f in data.get("features", []):
                props = f.get("properties", {})
                el_lat = props.get("lat")
                el_lon = props.get("lon")
                dist = haversine(lat, lon, el_lat, el_lon) if el_lat else 0
                restaurants.append({
                    "name": props.get("name", "Unnamed place"),
                    "amenity": props.get("amenity") or props.get("catering"),
                    "cuisine": props.get("cuisine"),
                    "address": props.get("formatted"),
                    "distance_m": round(dist),
                    "distance": f"{round(dist)} m",
                    "latitude": el_lat,
                    "longitude": el_lon
                })
            restaurants.sort(key=lambda x: x["distance_m"])
            return {"latitude": lat, "longitude": lon, "radius_m": radius_m, "count": len(restaurants), "restaurants": restaurants[:15]}
