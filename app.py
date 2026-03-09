import logging
from fastapi import FastAPI
from fastapi.responses import Response
import uvicorn
import os
from config import SMHI_API_URL, REFRESH_INTERVAL
from kml_generator import generate_kml
from data_fetcher import fetch_smhi_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ATAK Data Server")

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "ATAK Data Server",
        "version": "1.0.0"
    }

@app.get("/live-data.kml")
async def get_live_data():
    """
    Returns KML with live data from SMHI and other sources.
    ATAK clients pull this with the configured refresh interval.
    """
    try:
        logger.info("Fetching SMHI data...")
        data = await fetch_smhi_data()
        
        logger.info(f"Generating KML with {len(data)} data points...")
        kml_content = generate_kml(data, refresh_interval=REFRESH_INTERVAL)
        
        return Response(
            content=kml_content,
            media_type="application/vnd.google-earth.kml+xml",
            headers={
                "Content-Disposition": "attachment; filename=live-data.kml"
            }
        )
    except Exception as e:
        logger.error(f"Error generating KML: {e}")
        return Response(
            content=f"<kml xmlns='http://www.opengis.net/kml/2.2'><Document><name>Error</name></Document></kml>",
            media_type="application/vnd.google-earth.kml+xml",
            status_code=500
        )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
