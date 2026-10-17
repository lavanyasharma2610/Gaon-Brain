from fastapi import APIRouter
from app.sanjha import tractor_schedule, bijli_window, irrigation_slots

router = APIRouter()

@router.post("/tractor/schedule")
def ts(payload: dict):
    return tractor_schedule(payload.get("requests",[]))

@router.get("/power/window")
def pw():
    return bijli_window([])

@router.post("/water/slots")
def ws(payload: dict):
    return irrigation_slots(payload.get("plots",[]), payload.get("budget",10), payload.get("interval",5))
EOF