"""
Generates KML files from fetched data
"""
from lxml import etree
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
    # Root KML element
    kml = etree.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
    document = etree.SubElement(kml, 'Document')
    
    # Document metadata
    name = etree.SubElement(document, 'name')
    name.text = "ATAK Live Data Feed"
    
    description = etree.SubElement(document, 'description')
    description.text = f"Auto-refreshing data from SMHI and other sources. Last updated: {datetime.utcnow().isoformat()}Z"
    
    # Add NetworkLink for auto-refresh
    network_link = etree.SubElement(document, 'NetworkLink')
    nl_name = etree.SubElement(network_link, 'name')
    nl_name.text = "Live Updates"
    
    link = etree.SubElement(network_link, 'Link')
    href = etree.SubElement(link, 'href')
    href.text = "https://your-app.onrender.com/live-data.kml"  # Will be replaced with actual URL
    
    refresh_mode = etree.SubElement(link, 'refreshMode')
    refresh_mode.text = "onInterval"
    
    refresh_interval_elem = etree.SubElement(link, 'refreshInterval')
    refresh_interval_elem.text = str(refresh_interval)
    
    # Add placemarks for each data point
    for point in data_points:
        placemark = etree.SubElement(document, 'Placemark')
        
        pm_name = etree.SubElement(placemark, 'name')
        pm_name.text = point.get('name', 'Data Point')
        
        pm_description = etree.SubElement(placemark, 'description')
        pm_description.text = point.get('description', '')
        
        # Add coordinates
        point_elem = etree.SubElement(placemark, 'Point')
        coordinates = etree.SubElement(point_elem, 'coordinates')
        coordinates.text = f"{point.get('longitude', 0)},{point.get('latitude', 0)},0"
        
        # Optional: Add extended data
        if 'timestamp' in point:
            extended_data = etree.SubElement(placemark, 'ExtendedData')
            data_elem = etree.SubElement(extended_data, 'Data', name='timestamp')
            value = etree.SubElement(data_elem, 'value')
            value.text = point['timestamp']
    
    return etree.tostring(
        kml,
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8',
        standalone=True
    ).decode('utf-8')
