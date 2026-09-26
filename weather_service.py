import aiohttp
from typing import Dict, Any

WMO_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 51: "light drizzle", 61: "slight rain", 63: "moderate rain",
    65: "heavy rain", 80: "slight rain showers", 81: "moderate rain showers",
    95: "thunderstorm",
}

async def get_live_weather(lat: float, lon: float) -> Dict[str, Any]:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m,relative_humidity_2m",
        "timezone": "auto"
    }
    async with aiohttp.ClientSession() as s:
        async with s.get(url, params=params, timeout=10) as r:
            r.raise_for_status()
            j = await r.json()
            cur = j.get("current", {})
            code = cur.get("weather_code")
            return {
                "latitude": lat,
                "longitude": lon,
                "temperature": cur.get("temperature_2m"),
                "apparent_temperature": cur.get("apparent_temperature"),
                "conditions": WMO_CODES.get(code, f"weather code {code}"),
                "weather_code": code,
                "precipitation": cur.get("precipitation"),
                "rain": cur.get("rain"),
                "wind_speed": cur.get("wind_speed_10m"),
                "humidity": cur.get("relative_humidity_2m"),
                "is_raining": (cur.get("rain", 0) or 0) > 0,
            }
