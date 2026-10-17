from fastapi import APIRouter
from app.radar import haversine, alerts, heatmap
from app.providers import DiseaseProvider

router = APIRouter()
dp = DiseaseProvider()

@router.post("/radar/report")
def report(payload: dict):
    return {"status": "recorded", "data": payload}

@router.get("/radar/alerts")
def get_alerts():
    return alerts([])

@router.get("/radar/heatmap")
def get_heatmap():
    return heatmap([])

@router.post("/doctor/analyze")
def analyze(payload: dict):
    return dp.analyze(payload.get("condition","blight"), payload.get("confidence",0.8))
EOF