"""
Generates KML files from fetched data
"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def summarize_parameters(params):
    """
    Convert SMHI-style parameter list into a readable summary.
    Example: "Temp: 3.2°C, Wind: 5 m/s"
    """
    if not params:
        return ""

    lookup = {
        "t": "Temp",
        "ws": "Wind",
        "wd": "Wind Dir",
        "r": "Humidity",
        "msl": "Pressure",
    }

    parts = []
    for p in params:
        name = p.get("name")
        values = p.get("values", [])
        if not values:
            continue

        if name in lookup:
            parts.append(f"{lookup[name]}: {values[0]}")

    return ", ".join(parts)


def generate_kml(data_points, refresh_interval=60):
    """
    Generate KML document with NetworkLink for auto-refresh
    """
    kml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    kml += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    kml += '  <Document>\n'
    kml += '    <name>ATAK Live Data Feed</name>\n'
    kml += f'    <description>Auto-refreshing data feed. Last updated: {datetime.utcnow().isoformat()}Z</description>\n'

    for point in data_points:
        name = point.get("name", "Data Point")
        desc = point.get("description", "")
        lat = point.get("latitude", 0)
        lon = point.get("longitude", 0)
        params = summarize_parameters(point.get("parameters", []))

        full_description = desc
        if params:
            full_description += f"\n{params}"

        kml += '    <Placemark>\n'
        kml += f'      <name>{name}</name>\n'
        kml += f'      <description>{full_description}</description>\n'
        kml += '      <Point>\n'
        kml += f'        <coordinates>{lon},{lat},0</coordinates>\n'
        kml += '      </Point>\n'
        kml += '    </Placemark>\n'

    kml += '  </Document>\n'
    kml += '</kml>\n'

    return kml


# ---------------------------------------------------------
# NEW: Sweden Wind Heat Map KML Generator
# ---------------------------------------------------------

def wind_color(ws):
    """Return KML ARGB color based on wind speed."""
    if ws <= 5:
        return "ff00ff00"  # green
    if ws <= 10:
        return "ff00ffff"  # yellow
    if ws <= 15:
        return "ff00a5ff"  # orange
    return "ff0000ff"      # red


def wind_scale(ws):
    """Return icon scale based on wind speed."""
    if ws <= 5:
        return 0.8
    if ws <= 10:
        return 1.2
    if ws <= 15:
        return 1.6
    return 2.0


def generate_wind_kml(wind_points, refresh_interval=600):
    """
    Generate a Sweden-wide wind heat map KML.
    wind_points: list of dicts with lat, lon, ws, wd
    """

    kml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    kml += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    kml += '  <Document>\n'
    kml += '    <name>Sweden Wind Map</name>\n'
    kml += f'    <description>Wind heat map. Updated: {datetime.utcnow().isoformat()}Z</description>\n'

    for p in wind_points:
        lat = p["lat"]
        lon = p["lon"]
        ws = p["ws"]
        wd = p["wd"]
        color = wind_color(ws)
        scale = wind_scale(ws)

        kml += '    <Placemark>\n'
        kml += f'      <name>{ws} m/s</name>\n'
        kml += '      <Style>\n'
        kml += '        <IconStyle>\n'
        kml += f'          <heading>{wd}</heading>\n'
        kml += f'          <scale>{scale}</scale>\n'
        kml += f'          <color>{color}</color>\n'
        kml += '          <Icon>\n'
        kml += '            <href>http://localhost:8000/static/icons/wind-arrow.png</href>\n'
        kml += '          </Icon>\n'
        kml += '        </IconStyle>\n'
        kml += '      </Style>\n'
        kml += '      <Point>\n'
        kml += f'        <coordinates>{lon},{lat},0</coordinates>\n'
        kml += '      </Point>\n'
        kml += '    </Placemark>\n'

    kml += '  </Document>\n'
    kml += '</kml>\n'

    return kml

