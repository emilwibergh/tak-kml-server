"""
Data fetcher for weather and sensor providers.
Now includes Sweden-wide wind grid support with parallel fetching.
"""

import httpx
import logging
import time
import asyncio
from config import smhi_point_url

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Config for wind grid + caching
# ---------------------------------------------------------
GRID_STEP = 1.0          # degrees (1.0 is a good balance; use 0.5 for more detail)
WIND_CACHE_TTL = 1800    # seconds (30 minutes)
MAX_CONCURRENT_REQUESTS = 20  # limit parallel SMHI calls

# In-memory cache for wind grid
WIND_CACHE = {
    "timestamp": 0.0,
    "data": []
}


# ---------------------------------------------------------
# Generic JSON fetcher
# ---------------------------------------------------------
async def fetch_json(url: str):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching data from {url}: {e}")
        return None


# ---------------------------------------------------------
# SMHI wind parser (extract ws + wd)
# ---------------------------------------------------------
def parse_smhi_wind(data: dict, lat: float, lon: float):
    """
    Extract wind speed + direction from SMHI point forecast.
    Returns None if missing.
    """
    if not data or "timeSeries" not in data:
        return None

    ts = data["timeSeries"][0]  # first forecast step

    ws = None
    wd = None

    for p in ts["parameters"]:
        if p["name"] == "ws":
            ws = p["values"][0]
        elif p["name"] == "wd":
            wd = p["values"][0]

    if ws is None or wd is None:
        return None

    return {
        "lat": lat,
        "lon": lon,
        "ws": ws,
        "wd": wd,
        "timestamp": ts["validTime"],
    }


# ---------------------------------------------------------
# Sweden grid generator
# ---------------------------------------------------------
def generate_sweden_grid(step: float = GRID_STEP):
    lat_min, lat_max = 55.0, 69.5
    lon_min, lon_max = 11.0, 24.5

    points = []
    lat = lat_min
    while lat <= lat_max:
        lon = lon_min
        while lon <= lon_max:
            points.append((round(lat, 3), round(lon, 3)))
            lon += step
        lat += step

    return points


# ---------------------------------------------------------
# Parallel fetch for a single grid point
# ---------------------------------------------------------
async def _fetch_wind_for_point(lat: float, lon: float, sem: asyncio.Semaphore):
    url = smhi_point_url(lat, lon)
    async with sem:
        raw = await fetch_json(url)
    if not raw:
        return None
    return parse_smhi_wind(raw, lat, lon)


# ---------------------------------------------------------
# Public: fetch Sweden-wide wind grid (with caching)
# ---------------------------------------------------------
async def fetch_wind_grid():
    """
    Fetch wind data for a Sweden-wide grid.
    Uses parallel requests + 30-minute caching.
    """
    now = time.time()
    if now - WIND_CACHE["timestamp"] < WIND_CACHE_TTL and WIND_CACHE["data"]:
        return WIND_CACHE["data"]

    logger.info("Refreshing Sweden wind grid (parallel fetch)...")

    grid = generate_sweden_grid()
    sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    tasks = [
        _fetch_wind_for_point(lat, lon, sem)
        for lat, lon in grid
    ]

    results = await asyncio.gather(*tasks, return_exceptions=False)
    wind_points = [r for r in results if r is not None]

    WIND_CACHE["timestamp"] = now
    WIND_CACHE["data"] = wind_points

    logger.info(f"Wind grid updated: {len(wind_points)} points")
    return wind_points


# ---------------------------------------------------------
# Legacy single-point weather fetcher (kept for /live-data.kml)
# ---------------------------------------------------------
def parse_smhi_point_forecast(data: dict, lat: float, lon: float):
    """
    Convert SMHI forecast JSON into a list of unified data points.
    """
    points = []

    if not data or "timeSeries" not in data:
        return points

    for ts in data["timeSeries"][:5]:
        point = {
            "name": f"Forecast {ts['validTime']}",
            "description": "Weather forecast data",
            "latitude": lat,
            "longitude": lon,
            "timestamp": ts["validTime"],
            "parameters": ts["parameters"],
        }
        points.append(point)

    return points


async def fetch_weather_points():
    """
    Fetch and parse weather data for a single point (legacy endpoint).
    """
    lat, lon = 59.3, 18.0
    url = smhi_point_url(lat, lon)

    raw = await fetch_json(url)
    if raw is None:
        logger.error("No data returned from provider.")
        return []

    points = parse_smhi_point_forecast(raw, lat=lat, lon=lon)
    logger.info(f"Fetched {len(points)} weather points")
    return points

