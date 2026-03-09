"""
Configuration for ATAK Data Server
"""
import os

# ---------------------------------------------------------
# SMHI dynamic URL builder (point forecast)
# ---------------------------------------------------------
def smhi_point_url(lat: float, lon: float) -> str:
    """
    Build the SMHI point forecast URL for a given lat/lon.
    """
    return (
        "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/"
        "version/2/geotype/point/"
        f"lon/{lon}/lat/{lat}/data.json"
    )

# KML Refresh interval (in seconds)
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", 60))

# Server configuration
DEBUG = os.getenv("DEBUG", "False") == "True"

