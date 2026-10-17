from fastapi import APIRouter
from app.suraksha import sinchai_card, kharid_check, claim_kit

router = APIRouter()

@router.post("/suraksha/sinchai")
def sinchai(payload: dict):
    return {"result": sinchai_card(payload.get("plot",{}), payload.get("weather",{}), payload.get("crop_interval",5), payload.get("days_since",0), payload.get("health",1.0))}

@router.post("/suraksha/kharid")
def kharid(payload: dict):
    return kharid_check(payload.get("product",""), payload.get("mrp",0), payload.get("paid",0), payload.get("bill_received",False), payload.get("dealer",""))

@router.post("/suraksha/claim")
def claim(payload: dict):
    return claim_kit(payload.get("farmer",""), payload.get("policy",""), payload.get("survey",""), payload.get("crop",""), payload.get("area",0))
EOF