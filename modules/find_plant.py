from fastapi import APIRouter
from typing import Dict, List, Any

router = APIRouter()

# Sample plant database with Dutch values but English keys for frontend compatibility
PLANT_DATABASE = [
    {"name": "Sansevieria", "location": "binnen", "size": "medium", "style": "modern", "image": "image5.png"},
    {"name": "Ficus Lyrata", "location": "binnen", "size": "groot", "style": "minimalistisch", "image": "image8.png"},
    {"name": "Palmboom", "location": "buiten", "size": "groot", "style": "tropisch", "image": "image9.png"},
    {"name": "Epipremnum", "location": "kantoor", "size": "klein", "style": "modern", "image": "image10.png"},
    {"name": "Aloë Vera", "location": "binnen", "size": "klein", "style": "modern", "image": "image1.png"},
    {"name": "Calathea", "location": "binnen", "size": "medium", "style": "minimalistisch", "image": "image2.png"},
    {"name": "Dracaena", "location": "kantoor", "size": "groot", "style": "minimalistisch", "image": "image3.png"},
    {"name": "Monstera", "location": "kantoor", "size": "groot", "style": "tropisch", "image": "image4.png"},
    {"name": "Begonia", "location": "binnen", "size": "klein", "style": "modern", "image": "image6.png"},
    {"name": "Zamioculcas", "location": "kantoor", "size": "medium", "style": "modern", "image": "image7.png"}
]

@router.post("/find_plant")
def find_plant(user_input: Dict[str, str]) -> List[Dict[str, Any]]:
    # Expected input: {"location": "kantoor", "size": "klein", "style": "modern"}
    location = user_input.get("location", "").lower()
    size = user_input.get("size", "").lower()
    style = user_input.get("style", "").lower()

    matching_plants = [
        plant for plant in PLANT_DATABASE
        if plant["location"] == location and plant["size"] == size and plant["style"] == style
    ]
    
    if not matching_plants:
        return [{"message": "Sorry, geen perfecte match gevonden! Probeer je voorkeuren aan te passen."}]
    
    return matching_plants[:5]

