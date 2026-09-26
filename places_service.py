import aiohttp
import math
from typing import Dict, Any, List

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R*2*math.atan2(math.sqrt(a), math.sqrt(1-a))

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]

async def search_nearby(lat: float, lon: float, radius_m: int = 1000, category: str = "restaurant") -> Dict[str, Any]:
    tag_filter = '["amenity"~"restaurant|fast_food|cafe|food_court"]'
    query = f"""
    [out:json][timeout:15];
    ( node{tag_filter}(around:{radius_m},{lat},{lon}); way{tag_filter}(around:{radius_m},{lat},{lon}); );
    out center 20;
    """
    last_err = None
    for url in OVERPASS_URLS:
        try:
            async with aiohttp.ClientSession() as s:
                async with s.post(url, data={"data": query}, timeout=15) as r:
                    r.raise_for_status()
                    data = await r.json()
                    elements = data.get("elements", [])
                    restaurants: List[Dict] = []
                    for el in elements:
                        el_lat = el.get("lat") or el.get("center", {}).get("lat")
                        el_lon = el.get("lon") or el.get("center", {}).get("lon")
                        if not el_lat: continue
                        dist = haversine(lat, lon, el_lat, el_lon)
                        tags = el.get("tags", {})
                        restaurants.append({
                            "name": tags.get("name", "Unnamed place"),
                            "amenity": tags.get("amenity"),
                            "cuisine": tags.get("cuisine"),
                            "address": tags.get("addr:full") or f"{tags.get('addr:street','')} {tags.get('addr:housenumber','')}".strip(),
                            "distance_m": round(dist),
                            "distance": f"{round(dist)} m",
                            "latitude": el_lat,
                            "longitude": el_lon
                        })
                    restaurants.sort(key=lambda x: x["distance_m"])
                    return {"latitude": lat, "longitude": lon, "radius_m": radius_m, "count": len(restaurants), "restaurants": restaurants[:15]}
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"Places API failed: {last_err}")
