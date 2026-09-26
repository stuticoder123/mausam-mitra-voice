from loguru import logger
from pipecat.services.llm_service import FunctionCallParams
from location_service import LocationStore, geocode_city, reverse_geocode
from weather_service import get_live_weather
from places_service import search_nearby

store = LocationStore()

async def get_current_location(params: FunctionCallParams):
    """Get the user's current location. Use when user says 'near me', 'around me', 'where am I', 'my location'."""
    try:
        loc = await store.get_last()
        if not loc:
            await params.result_callback({"error": "location_unavailable", "message": "Current location not available."})
            return
        try:
            rev = await reverse_geocode(loc["latitude"], loc["longitude"])
            await params.result_callback(rev)
        except Exception as e:
            logger.warning(f"Reverse geocode failed {e}")
            await params.result_callback(loc)
    except Exception as e:
        await params.result_callback({"error": str(e)})

async def get_current_weather(params: FunctionCallParams):
    """Get live weather for current user location. Use when user says 'weather around me', 'temperature around me'."""
    try:
        loc = await store.get_last()
        if not loc:
            await params.result_callback({"error": "location_unavailable", "need_city": True})
            return
        weather = await get_live_weather(loc["latitude"], loc["longitude"])
        try:
            rev = await reverse_geocode(loc["latitude"], loc["longitude"])
            weather["city"] = rev.get("city")
        except: pass
        await params.result_callback(weather)
    except Exception as e:
        await params.result_callback({"error": "weather_fetch_failed", "message": str(e)})

async def get_weather_by_location(params: FunctionCallParams, location: str):
    """Get live weather for an explicit city like 'Jaipur', 'Delhi'. Geocodes first."""
    try:
        geo = await geocode_city(location)
        weather = await get_live_weather(geo["latitude"], geo["longitude"])
        weather.update({"requested_location": location, "resolved_city": geo["city"], "display_name": geo["display_name"]})
        await params.result_callback(weather)
    except Exception as e:
        await params.result_callback({"error": "geocode_or_weather_failed", "location": location, "message": str(e)})

async def search_nearby_restaurants(params: FunctionCallParams, radius_m: int = 1000):
    """Search real nearby restaurants. Use for 'restaurants near me', 'find food around me'. radius in meters."""
    try:
        loc = await store.get_last()
        if not loc:
            await params.result_callback({"error": "location_unavailable"})
            return
        if radius_m < 100: radius_m = 100
        if radius_m > 10000: radius_m = 10000
        result = await search_nearby(loc["latitude"], loc["longitude"], radius_m)
        await params.result_callback(result)
    except Exception as e:
        await params.result_callback({"error": "places_fetch_failed", "message": str(e)})
