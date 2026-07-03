from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from collections import Counter

app = FastAPI()

# Разрешаем подключения с твоего сайта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# База данных в памяти
DATABASE = {
    "ultimate123": {
        "votes": []
    }
}

class VoteModel(BaseModel):
    name: str
    slots: List[str]
    location: str

@app.post("/api/vote/{meeting_id}")
async def collect_vote(meeting_id: str, data: VoteModel):
    if meeting_id not in DATABASE:
        DATABASE[meeting_id] = {"votes": []}
    
    # Сохраняем голос
    DATABASE[meeting_id]["votes"].append({
        "name": data.name,
        "slots": data.slots,
        "location": data.location
    })
    
    return {"status": "success", "message": "Ваш голос принят!"}

@app.get("/api/results/{meeting_id}")
async def get_results(meeting_id: str):
    votes = DATABASE.get(meeting_id, {}).get("votes", [])
    if not votes:
        return {"message": "Голосов пока нет"}
    
    # Считаем популярность времени
    all_slots = [slot for v in votes for slot in v["slots"]]
    slot_counts = Counter(all_slots).most_common(5)
    
    # Считаем популярность локаций
    all_locs = [v["location"] for v in votes if v["location"]]
    loc_counts = Counter(all_locs).most_common(3)
    
    return {
        "top_slots": slot_counts,
        "top_locations": loc_counts
    }
