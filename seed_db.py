import google.auth
from google.cloud import firestore

# IMPORTANT: Hardcoded Project ID string to avoid project number issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-02-c99d4be278a4"

def seed():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    print(f"Connecting to Firestore with project ID: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID, credentials=credentials)
    
    destinations_ref = db.collection("destinations")
    
    sample_destinations = [
        {
            "id": "dest_sf",
            "name": "San Francisco",
            "city": "San Francisco",
            "country": "USA",
            "category": "Culture & Sights",
            "description": "Iconic Golden Gate Bridge, historic cable cars, vibrant food scene, and coastal fog.",
            "rating": 4.7,
            "avg_cost_per_day": 250,
            "popular_activities": ["Golden Gate Bridge Walk", "Alcatraz Island Tour", "Fisherman's Wharf"]
        },
        {
            "id": "dest_tokyo",
            "name": "Tokyo",
            "city": "Tokyo",
            "country": "Japan",
            "category": "Metropolis & Culinary",
            "description": "Ultra-modern skyscrapers, ancient temples, world-class cuisine, and neon-lit night life.",
            "rating": 4.9,
            "avg_cost_per_day": 200,
            "popular_activities": ["Senso-ji Temple", "Shibuya Crossing", "Tsukiji Outer Market"]
        },
        {
            "id": "dest_paris",
            "name": "Paris",
            "city": "Paris",
            "country": "France",
            "category": "Romance & Art",
            "description": "The City of Light known for the Eiffel Tower, Louvre Museum, chic cafes, and art fashion.",
            "rating": 4.8,
            "avg_cost_per_day": 230,
            "popular_activities": ["Louvre Museum", "Eiffel Tower Sunset", "Seine River Cruise"]
        },
        {
            "id": "dest_kyoto",
            "name": "Kyoto",
            "city": "Kyoto",
            "country": "Japan",
            "category": "Heritage & Nature",
            "description": "Famous for classical Buddhist temples, gardens, imperial palaces, Shinto shrines, and traditional wooden houses.",
            "rating": 4.9,
            "avg_cost_per_day": 180,
            "popular_activities": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji (Golden Pavilion)"]
        }
    ]
    
    for item in sample_destinations:
        doc_ref = destinations_ref.document(item["id"])
        doc_ref.set(item)
        print(f"Seeded destination: {item['name']} ({item['id']})")

if __name__ == "__main__":
    seed()
