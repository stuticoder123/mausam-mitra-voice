import os
import aiohttp
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

async def get_live_weather(lat: float, lon: float) -> Dict[str, Any]:
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY not found in.env")

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric" # for Celsius
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=10) as r:
            r.raise_for_status()
            j = await r.json()

            main = j.get("main", {})
            weather = j.get("weather", [{}])[0]
            wind = j.get("wind", {})
            rain = j.get("rain", {})

            return {
                "latitude": lat,
                "longitude": lon,
                "temperature": main.get("temp"),
                "apparent_temperature": main.get("feels_like"),
                "conditions": weather.get("description", "unknown"),
                "weather_code": weather.get("main"),
                "humidity": main.get("humidity"),
                "wind_speed": wind.get("speed"),
                "precipitation": rain.get("1h", 0),
                "is_raining": "rain" in j or rain.get("1h", 0) > 0,
                "city": j.get("name"),
                "source": "openweathermap"
            }
