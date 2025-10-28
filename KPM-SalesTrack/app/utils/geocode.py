import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEOCODE_API_KEY = os.getenv("GEOCODE_EARTH_API")

def geocode_address(address, country_code="KE"):
    if not address:
        return None

    url = "https://api.geocode.earth/v1/search"
    params = {
        "text": address,
        "api_key": GEOCODE_API_KEY,
        "boundary.country": country_code
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("features") and isinstance(data["features"], list):
            feature = data["features"][0]
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [])

            return {
                "name": props.get("name"),
                "label": props.get("label"),
                "coordinates": coords,
                "type": props.get("layer")
            }

        print(f"No features found for address: {address}")
        return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status: {response.status_code}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

        
def reverse_geocode(lat, lon, country_code="KE"):
    if lat is None or lon is None:
        return None

    url = "https://api.geocode.earth/v1/reverse"
    params = {
        "point.lat": lat,
        "point.lon": lon,
        "api_key": GEOCODE_API_KEY,
        "boundary.country": country_code
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("features") and isinstance(data["features"], list):
            feature = data["features"][0]
            props = feature.get("properties", {})
            coords = feature.get("geometry", {}).get("coordinates", [])

            return {
                "name": props.get("name"),
                "label": props.get("label"),
                "coordinates": coords,
                "type": props.get("layer")
            }

        print(f"No features found for coordinates: {lat}, {lon}")
        return None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status: {response.status_code}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None    