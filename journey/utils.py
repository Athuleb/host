import socket
def is_internet_available():
    try:
        # Try connecting to a public DNS server (e.g., Google's DNS).
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False
    
import requests
from django.http import JsonResponse
import random






def fetch_destination_details():
    destination_names = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", 
    "Gujarat", "Haryana", "Himachal Pradesh", "Jammu and Kashmir", "Jharkhand", 
    "Karnataka", "Kerala", "Ladakh", "Madhya Pradesh", "Maharashtra", "Manipur", 
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", 
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
]
    random_destinations = random.sample(destination_names, 12)

    destination_names = random_destinations
    random.shuffle(destination_names)
    base_url = "https://en.wikipedia.org/api/rest_v1/page/summary/"
    destinations = []

    for destination in destination_names:
        url = f"{base_url}{destination.replace(' ', '_')}"  
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                id = len(destinations) +1
                destinations.append({
                    "id": id,
                    "location": destination,
                    "description": data.get("extract", "No description available"),
                    "image": data.get("thumbnail", {}).get("source", None),
                    "wiki_url": data.get("content_urls", {}).get("desktop", {}).get("page", None)
                })
            else:
                destinations.append({
                    "location": destination,
                    "description": "No details available",
                    "image": None,
                    "wiki_url": None
                })
        except requests.exceptions.RequestException:
            destinations.append({
                "location": destination,
                "description": "Error fetching details",
                "image": None,
                "wiki_url": None
            })
    
    return destinations


