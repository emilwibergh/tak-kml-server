import logging
import os
import asyncio

from fastapi import FastAPI
from fastapi.responses import Response
import uvicorn

from config import REFRESH_INTERVAL
from kml_generator import generate_kml, generate_wind_kml
from data_fetcher import fetch_weather_points, fetch_wind_grid, WIND_CACHE_TTL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ATAK Data Server")

# In-memory pre-generated KML cache for Sweden wind map
WIND_KML_CACHE = {
    "content": None,
    "timestamp": 0.0,
}


@app.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": "ATAK Data Server",
        "version": "1.0.0",
    }


# ---------------------------------------------------------
# Existing SMHI single-point feed
# ---------------------------------------------------------
@app.get("/live-data.kml")
async def get_live_data():
    try:
        logger.info("Fetching SMHI data...")
        data = await fetch_weather_points()

        logger.info(f"Generating KML with {len(data)} data points...")
        kml_content = generate_kml(data, refresh_interval=REFRESH_INTERVAL)

        return Response(
            content=kml_content,
            media_type="application/vnd.google-earth.kml+xml",
            headers={"Content-Disposition": "attachment; filename=live-data.kml"},
        )
    except Exception as e:
        logger.error(f"Error generating KML: {e}")
        return Response(
            content="<kml xmlns='http://www.opengis.net/kml/2.2'><Document><name>Error</name></Document></kml>",
            media_type="application/vnd.google-earth.kml+xml",
            status_code=500,
        )


# ---------------------------------------------------------
# Background task: pre-generate Sweden wind KML in memory
# ---------------------------------------------------------
async def wind_kml_background_updater():
    """
    Periodically refresh the Sweden wind KML and store it in memory.
    """
    await asyncio.sleep(2)  # small delay to let app start cleanly
    while True:
        try:
            logger.info("Background: updating Sweden wind grid + KML...")
            wind_points = await fetch_wind_grid()
            kml_content = generate_wind_kml(wind_points)

            WIND_KML_CACHE["content"] = kml_content
            WIND_KML_CACHE["timestamp"] = asyncio.get_event_loop().time()

            logger.info(
                f"Background: Sweden wind KML updated ({len(wind_points)} points)."
            )
        except Exception as e:
            logger.error(f"Background wind KML update failed: {e}")

        # Sleep same as wind cache TTL so we don't over-fetch
        await asyncio.sleep(WIND_CACHE_TTL)


@app.on_event("startup")
async def startup_event():
    """
    Start background task to keep wind KML fresh in memory.
    """
    asyncio.create_task(wind_kml_background_updater())


# ---------------------------------------------------------
# Sweden Wind Heat Map endpoint (instant, uses pre-generated KML)
# ---------------------------------------------------------
@app.get("/wind-sweden.kml")
async def get_wind_sweden():
    """
    Returns a Sweden-wide wind heat map KML.
    Served from in-memory pre-generated cache.
    """
    try:
        # If cache is empty (e.g., just started), generate once on-demand
        if not WIND_KML_CACHE["content"]:
            logger.info("No cached wind KML yet, generating once on-demand...")
            wind_points = await fetch_wind_grid()
            WIND_KML_CACHE["content"] = generate_wind_kml(wind_points)

        return Response(
            content=WIND_KML_CACHE["content"],
            media_type="application/vnd.google-earth.kml+xml",
            headers={"Content-Disposition": "attachment; filename=wind-sweden.kml"},
        )
    except Exception as e:
        logger.error(f"Error serving wind KML: {e}")
        return Response(
            content="<kml xmlns='http://www.opengis.net/kml/2.2'><Document><name>Error</name></Document></kml>",
            media_type="application/vnd.google-earth.kml+xml",
            status_code=500,
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

