import os
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

def get_maps_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is missing.")
    return key


def geocode_address(address: str) -> Dict[str, Any]:
    """Geocode a physical address or city name into geographic coordinates (latitude and longitude).

    Args:
        address: The address or place name to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'San Francisco').

    Returns:
        A dictionary with formatted address, latitude, and longitude.
    """
    api_key = get_maps_api_key()
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        if not results:
            return {"error": f"No coordinates found for address '{address}'."}
        
        first_res = results[0]
        location = first_res.get("geometry", {}).get("location", {})
        
        return {
            "address": address,
            "formatted_address": first_res.get("formatted_address"),
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
        }
    except Exception as e:
        return {"error": f"Geocoding failed for '{address}': {str(e)}"}


def search_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius: float = 1000.0,
) -> List[Dict[str, Any]]:
    """Search for nearby places of a specific type around a latitude/longitude coordinate using Google Places API (New).

    Args:
        latitude: Latitude coordinate (e.g., 37.7749).
        longitude: Longitude coordinate (e.g., -122.4194).
        place_type: Type of place to search for (e.g., 'restaurant', 'cafe', 'tourist_attraction', 'museum', 'hotel', 'park').
        radius: Radius in meters around the coordinate (default: 1000.0).

    Returns:
        A list of nearby places with key fields: name, address, and location.
    """
    api_key = get_maps_api_key()
    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types",
    }
    
    body = {
        "includedTypes": [place_type.lower()],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius),
            }
        },
    }
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        places = data.get("places", [])
        results = []
        for place in places:
            display_name = place.get("displayName", {}).get("text")
            address = place.get("formattedAddress")
            location = place.get("location")
            results.append({
                "name": display_name,
                "address": address,
                "location": location,
                "types": place.get("types", []),
            })
        return results
    except Exception as e:
        return [{"error": f"Nearby places search failed: {str(e)}"}]
