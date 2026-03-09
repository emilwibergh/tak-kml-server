"""
Fetches data from SMHI and other APIs
"""
import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

async def fetch_smhi_data():
    """
    Fetch weather data from SMHI API
    
    Returns:
        list: List of data points with coordinates and metadata
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Example: Fetching point data from Stockholm, Sweden
            url = "https://opendata-download-metanalysis.smhi.se/api/category/mesan1g/version/2/geoType/point/lon/18.0/lat/59.3/data.json"
            
            response = await client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse and transform SMHI data
            points = []
            
            # Example: Extract temperature data
            if "timeSeries" in data:
                for ts in data["timeSeries"][:5]:  # Limit to first 5 points
                    if ts["parameters"]:
                        point = {
                            "name": f"Weather at {ts['validTime'][:10]}",
                            "description": f"SMHI Data Point",
                            "latitude": 59.3,
                            "longitude": 18.0,
                            "timestamp": ts["validTime"],
                            "parameters": ts["parameters"]
                        }
                        points.append(point)
            
            logger.info(f"Fetched {len(points)} data points from SMHI")
            return points
            
    except Exception as e:
        logger.error(f"Error fetching SMHI data: {e}")
        return []

async def fetch_webpage_data(url: str):
    """
    Fetch and parse data from a webpage
    
    Args:
        url: URL of the webpage to scrape
        
    Returns:
        list: Extracted data points
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            # Add parsing logic here based on webpage structure
            return []
    except Exception as e:
        logger.error(f"Error fetching webpage {url}: {e}")
        return []
