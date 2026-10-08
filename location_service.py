import asyncio
import aiohttp
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv(override=True)

GEOAPIFY_KEY = os.getenv("GEOAPIFY_API_KEY")

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

async def geocode_city(city: str) -> Dict[str, Any]:
    url = f"https://api.geoapify.com/v1/geocode/search?text={city}&apiKey={GEOAPIFY_KEY}&limit=1"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, timeout=10) as r:
            r.raise_for_status()
            data = await r.json()
            if not data.get("features"):
                raise ValueError(f"City not found: {city}")
            props = data["features"][0]["properties"]
            return {
                "latitude": props["lat"],
                "longitude": props["lon"],
                "city": props.get("city") or city,
                "state": props.get("state"),
                "country": props.get("country"),
                "display_name": props.get("formatted")
            }

async def reverse_geocode(lat: float, lon: float) -> Dict[str, Any]:
    url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={GEOAPIFY_KEY}"
    async with aiohttp.ClientSession() as s:
        async with s.get(url, timeout=10) as r:
            r.raise_for_status()
            data = await r.json()
            props = data["features"][0]["properties"] if data.get("features") else {}
            return {
                "latitude": lat,
                "longitude": lon,
                "city": props.get("city") or props.get("county"),
                "state": props.get("state"),
                "country": props.get("country"),
                "display_name": props.get("formatted")
            }
