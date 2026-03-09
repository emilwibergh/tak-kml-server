"""
Generates KML files from fetched data
"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def generate_kml(data_points, refresh_interval=60):
    """
    Generate KML document with NetworkLink for auto-refresh
    
    Args:
        data_points: List of data points with lat/lon/name/description
        refresh_interval: Seconds between ATAK refresh requests
        
    Returns:
        str: KML XML content
    """
    kml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    kml += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    kml += '  <Document>\n'
    kml += '    <name>ATAK Live Data Feed</name>\n'
    kml += f'    <description>Auto-refreshing data from SMHI and other sources. Last updated: {datetime.utcnow().isoformat()}Z</description>\n'
    
    # Add placemarks for each data point
    for point in data_points:
        kml += '    <Placemark>\n'
        kml += f'      <name>{point.get("name", "Data Point")}</name>\n'
        kml += f'      <description>{point.get("description", "")}</description>\n'
        kml += '      <Point>\n'
        kml += f'        <coordinates>{point.get("longitude", 0)},{point.get("latitude", 0)},0</coordinates>\n'
        kml += '      </Point>\n'
        kml += '    </Placemark>\n'
    
    kml += '  </Document>\n'
    kml += '</kml>\n'
    
    return kml
