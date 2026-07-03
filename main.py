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
    
    # Считаем популярность времени + имена проголосовавших
    slot_names = {}
    for v in votes:
        for slot in v["slots"]:
            slot_names.setdefault(slot, []).append(v["name"])

    slot_counts = Counter({s: len(names) for s, names in slot_names.items()}).most_common(5)
    top_slots = [{"slot": s, "count": c, "names": slot_names[s]} for s, c in slot_counts]

    # Считаем популярность локаций + имена
    loc_names = {}
    for v in votes:
        if v["location"]:
            loc_names.setdefault(v["location"], []).append(v["name"])

    loc_counts = Counter({l: len(names) for l, names in loc_names.items()}).most_common(3)
    top_locations = [{"location": l, "count": c, "names": loc_names[l]} for l, c in loc_counts]

    return {
        "top_slots": top_slots,
        "top_locations": top_locations
    }
