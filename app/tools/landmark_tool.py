from typing import Dict, Any
import requests

def get_place_summary(location_name: str) -> Dict[str, Any]:
    """Fetch real-time encyclopedic summary, description, and thumbnail image for any travel destination, city, or landmark.

    Args:
        location_name: Name of the destination, city, or landmark (e.g., 'Eiffel Tower', 'Kyoto', 'Golden Gate Bridge', 'Colosseum').

    Returns:
        A dictionary containing title, summary extract, description, thumbnail image URL, and official article link.
    """
    formatted_title = location_name.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{formatted_title}"
    headers = {"User-Agent": "TravelConciergeBot/1.0 (contact@travelconcierge.app)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            return {"error": f"No landmark or location info found for '{location_name}'."}
        response.raise_for_status()
        data = response.json()
        
        return {
            "title": data.get("title", location_name),
            "description": data.get("description", ""),
            "summary": data.get("extract", "No detailed summary available."),
            "image_url": data.get("thumbnail", {}).get("source"),
            "wikipedia_url": data.get("content_urls", {}).get("desktop", {}).get("page"),
        }
    except Exception as e:
        return {"error": f"Failed to fetch place summary for '{location_name}': {str(e)}"}
