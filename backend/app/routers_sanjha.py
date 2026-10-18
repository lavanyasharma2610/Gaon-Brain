from fastapi import APIRouter
from sqlmodel import select

from app.db import get_session
from app.models import Farmer, Plot, PowerLog, TractorRequest
from app.sanjha import bijli_window, irrigation_slots, tractor_schedule

router = APIRouter()

@router.get("/tractor/schedule")
@router.post("/tractor/schedule")
def ts(payload: dict | None = None):
    payload = payload or {}
    reqs = payload.get("requests")
    if not reqs:
        db = get_session()
        try:
            db_reqs = db.exec(select(TractorRequest)).all()
            farmers = {f.id: f.name for f in db.exec(select(Farmer)).all()}
            reqs = [
                {
                    "id": r.id,
                    "farmer_id": r.farmer_id,
                    "farmer_name": farmers.get(r.farmer_id, f"किसान {r.farmer_id}"),
                    "want_date": r.want_date,
                    "prev_served_count": r.prev_served_count,
                    "hours": 4.0
                }
                for r in db_reqs
            ]
        finally:
            db.close()
    
    tractors = payload.get("tractors_count", 3)
    hours_per_tractor = payload.get("hours_per_tractor", 8)
    return tractor_schedule(reqs, tractors_count=tractors, hours_per_tractor=hours_per_tractor)

@router.get("/power/window")
@router.post("/power/window")
def pw(payload: dict | None = None):
    payload = payload or {}
    feeder_id = payload.get("feeder_id")
    
    db = get_session()
    try:
        query = select(PowerLog)
        if feeder_id:
            query = query.where(PowerLog.feeder_id == feeder_id)
        logs = db.exec(query).all()
        log_dicts = [{"hour": l.hour, "on_days": l.on_days, "total_days": l.total_days} for l in logs]
    finally:
        db.close()
        
    return bijli_window(log_dicts)

@router.get("/water/slots")
@router.post("/water/slots")
def ws(payload: dict | None = None):
    payload = payload or {}
    plots = payload.get("plots")
    if not plots:
        db = get_session()
        try:
            db_plots = db.exec(select(Plot)).all()
            farmers = {f.id: f.name for f in db.exec(select(Farmer)).all()}
            plots = [
                {
                    "id": p.id,
                    "farmer_id": p.farmer_id,
                    "farmer_name": farmers.get(p.farmer_id, f"किसान {p.farmer_id}"),
                    "area_acre": p.area_acre,
                    "crop": p.crop,
                    "health": p.health,
                    "feeder_id": p.feeder_id or 1
                }
                for p in db_plots
            ]
        finally:
            db.close()

    budget = payload.get("budget", 18.0)
    rain = payload.get("rain_mm", 0.0)
    return irrigation_slots(plots, budget_hours=budget, weather_rain_mm=rain)
