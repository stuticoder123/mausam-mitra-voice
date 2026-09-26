import asyncio
import aiohttp
from loguru import logger
from typing import Optional, Dict, Any
import os

class LocationStore:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = {}
            cls._instance._lock = asyncio.Lock()
        return cls._instance

    async def set_last(self, lat: float, lon: float):
        async with self._lock:
            self._data["__last__"] = {"latitude": lat, "longitude": lon}

    async def get_last(self):
        async with self._lock:
            return self._data.get("__last__")

USER_AGENT = os.getenv("NOMINATIM_USER_AGENT", "stuti-voice-assistant/1.0")

async def geocode_city(city: str) -> Dict[str, Any]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city, "format": "json", "limit": 1, "addressdetails": 1}
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params, headers=headers, timeout=10) as r:
            r.raise_for_status()
            data = await r.json()
            if not data:
                raise ValueError(f"City not found: {city}")
            item = data[0]
            return {
                "latitude": float(item["lat"]),
                "longitude": float(item["lon"]),
                "city": item.get("address", {}).get("city") or item.get("address", {}).get("town") or city,
                "state": item.get("address", {}).get("state"),
                "country": item.get("address", {}).get("country"),
                "display_name": item.get("display_name")
            }

async def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json", "addressdetails": 1, "zoom": 10}
    headers = {"User-Agent": USER_AGENT}
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params, headers=headers, timeout=10) as r:
            r.raise_for_status()
            item = await r.json()
            addr = item.get("address", {})
            return {
                "latitude": lat,
                "longitude": lon,
                "city": addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county"),
                "state": addr.get("state"),
                "country": addr.get("country"),
                "display_name": item.get("display_name"),
            }
