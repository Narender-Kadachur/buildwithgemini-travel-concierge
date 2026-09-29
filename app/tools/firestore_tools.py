import uuid
from typing import Optional, List, Dict, Any
from google.cloud import firestore

# IMPORTANT: Hardcoded Project ID string to avoid project number issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-02-c99d4be278a4"

def get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)

def list_destinations(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List travel destinations from Firestore database.

    Args:
        category: Optional category filter (e.g. 'Culture & Sights', 'Metropolis & Culinary', 'Romance & Art', 'Heritage & Nature').

    Returns:
        A list of destination dictionaries.
    """
    db = get_firestore_client()
    query_ref = db.collection("destinations")
    
    if category:
        docs = query_ref.where("category", "==", category).stream()
    else:
        docs = query_ref.stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_destination_details(destination_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific travel destination from Firestore.

    Args:
        destination_id: The unique document ID of the destination (e.g. 'dest_sf', 'dest_tokyo').

    Returns:
        Dictionary containing destination details or an error message if not found.
    """
    db = get_firestore_client()
    doc_ref = db.collection("destinations").document(destination_id)
    doc = doc_ref.get()
    
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return {"error": f"Destination with ID '{destination_id}' not found."}


def add_destination(
    name: str,
    city: str,
    country: str,
    category: str,
    description: str,
    rating: float = 4.5,
    avg_cost_per_day: int = 200,
    popular_activities: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Add a new travel destination to the Firestore database.

    Args:
        name: Name of the destination.
        city: City name.
        country: Country name.
        category: Category (e.g., 'Adventure', 'Beach', 'Culture').
        description: A brief summary or description of the destination.
        rating: Rating out of 5.0 (e.g., 4.8).
        avg_cost_per_day: Estimated average daily cost in USD.
        popular_activities: A list of key activities/attractions.

    Returns:
        A dictionary with status and the newly created destination ID.
    """
    db = get_firestore_client()
    doc_id = f"dest_{name.lower().replace(' ', '_')}"
    doc_ref = db.collection("destinations").document(doc_id)
    
    destination_data = {
        "id": doc_id,
        "name": name,
        "city": city,
        "country": country,
        "category": category,
        "description": description,
        "rating": float(rating),
        "avg_cost_per_day": int(avg_cost_per_day),
        "popular_activities": popular_activities or [],
    }
    
    doc_ref.set(destination_data)
    return {"status": "success", "message": f"Added destination '{name}'", "destination_id": doc_id}
