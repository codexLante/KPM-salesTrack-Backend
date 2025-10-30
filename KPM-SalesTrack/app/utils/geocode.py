import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()
GEOCODE_API_KEY = os.getenv("GEOCODE_EARTH_API")

logger = logging.getLogger(__name__)


def geocode_address(address, country_code="KE"):

    if not address:
        logger.warning("geocode_address called with empty address")
        return None
    
    if not GEOCODE_API_KEY:
        logger.error("GEOCODE_EARTH_API key not found in environment variables")
        return None

    url = "https://api.geocode.earth/v1/search"
    params = {
        "text": address,
        "api_key": GEOCODE_API_KEY,
        "boundary.country": country_code
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("features") and isinstance(data["features"], list) and len(data["features"]) > 0:
            feature = data["features"][0]
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [])

            if not coords or len(coords) < 2:
                logger.error(f"Invalid coordinates received for address: {address}")
                return None

            return {
                "name": props.get("name"),
                "label": props.get("label"),
                "coordinates": coords,
                "type": props.get("layer")
            }

        logger.warning(f"No features found for address: {address}")
        return None

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error geocoding address: {address}")
        return None
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err} - Status: {response.status_code}")
        return None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
        return None
    except ValueError as json_err:
        logger.error(f"JSON decode error: {json_err}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error geocoding address: {e}")
        return None


def reverse_geocode(lat, lon, country_code="KE"):

    if lat is None or lon is None:
        logger.warning("reverse_geocode called with None coordinates")
        return None
    
    try:
        lat = float(lat)
        lon = float(lon)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            logger.error(f"Invalid coordinate ranges: lat={lat}, lon={lon}")
            return None
    except (ValueError, TypeError):
        logger.error(f"Invalid coordinate types: lat={lat}, lon={lon}")
        return None
    
    if not GEOCODE_API_KEY:
        logger.error("GEOCODE_EARTH_API key not found in environment variables")
        return None

    url = "https://api.geocode.earth/v1/reverse"
    params = {
        "point.lat": lat,
        "point.lon": lon,
        "api_key": GEOCODE_API_KEY,
        "boundary.country": country_code
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("features") and isinstance(data["features"], list) and len(data["features"]) > 0:
            feature = data["features"][0]
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [])

            if not coords or len(coords) < 2:
                logger.error(f"Invalid coordinates received for reverse geocode: lat={lat}, lon={lon}")
                return None

            return {
                "name": props.get("name"),
                "label": props.get("label"),
                "coordinates": coords,
                "type": props.get("layer")
            }

        logger.warning(f"No features found for coordinates: lat={lat}, lon={lon}")
        return None

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error reverse geocoding coordinates: lat={lat}, lon={lon}")
        return None
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err} - Status: {response.status_code}")
        return None
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Request error occurred: {req_err}")
        return None
    except ValueError as json_err:
        logger.error(f"JSON decode error: {json_err}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error reverse geocoding: {e}")
        return None