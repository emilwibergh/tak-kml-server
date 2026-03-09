"""
Configuration for ATAK Data Server
"""
import os

# SMHI API Configuration
SMHI_API_URL = os.getenv(
    "SMHI_API_URL",
    "https://opendata-download-metanalysis.smhi.se/api/category/mesan1g/version/2/geoType/point/lon/18.0/lat/59.3/data.json"
)

# KML Refresh interval (in seconds)
# How often ATAK clients will pull updated data
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 60))

# Server configuration
DEBUG = os.getenv("DEBUG", "False") == "True"
