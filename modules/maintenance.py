from fastapi import APIRouter
import openai
import os

router = APIRouter()

# Predefined maintenance tips in Dutch
maintenance_tips = {
    "cleaning": "Gebruik een zachte doek of een plumeau om stof te verwijderen. Voor een grondigere reiniging, gebruik milde zeep en water.",
    "uv_protection": "Om vervaging te voorkomen, plaats kunstplanten in schaduwrijke gebieden of gebruik een UV-bestendige spray.",
    "sustainability": "Onze planten zijn gemaakt van milieuvriendelijke materialen. Overweeg om oude planten te hergebruiken in plaats van ze weg te gooien."
}

@router.get("/maintenance/{topic}")
def get_maintenance_tips(topic: str):
    topic = topic.lower()
    if topic in maintenance_tips:
        return {
            "message": f"Hier is wat je moet weten over {topic.replace('_', ' ')}:",
            "tip": maintenance_tips[topic]
        }
    else:
        return {
            "message": "Sorry, ik heb geen informatie over dit onderwerp. Probeer cleaning, uv_protection of sustainability."
        }

@router.get("/maintenance/plant/{plant_name}")
def get_plant_maintenance(plant_name: str):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Je bent een expert op plantenonderhoud."},
            {"role": "user", "content": f"Hoe onderhoud ik {plant_name}?"}
        ]
    )
    
    tip = response["choices"][0]["message"]["content"]
    return {
        "message": f"Hier is wat je moet weten over het onderhoud van {plant_name}:",
        "tip": tip
    }

# Zorg voor compatibiliteit met app.py
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

