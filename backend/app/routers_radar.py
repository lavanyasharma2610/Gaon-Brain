import json
from datetime import datetime, timezone
from fastapi import APIRouter
from sqlmodel import select

from app.db import get_session
from app.models import Event, Report
from app.radar import REMEDIES_TABLE, compute_alerts, compute_heatmap

router = APIRouter()

@router.post("/radar/report")
def report(payload: dict):
    db = get_session()
    try:
        rep_type = payload.get("type", "disease")
        subtype = payload.get("subtype", payload.get("condition", "blight"))
        notes = payload.get("notes", "")
        farmer_name = payload.get("farmer_name", "राम कुमार")
        plot_id = payload.get("plot_id", 1)
        lat = payload.get("lat", 28.615)
        lon = payload.get("lon", 77.210)
        
        rep = Report(
            type=rep_type,
            payload=json.dumps({
                "subtype": subtype,
                "notes": notes,
                "farmer_name": farmer_name,
                "plot_id": plot_id,
                "lat": lat,
                "lon": lon,
                "ts": datetime.now(timezone.utc).isoformat()
            })
        )
        db.add(rep)
        
        event = Event(
            type="disease_report" if rep_type == "disease" else "animal_sighting",
            plot_id=plot_id,
            lat=lat,
            lon=lon,
            raw_text=f"{rep_type}: {subtype} reported on plot {plot_id}",
            payload=json.dumps({"subtype": subtype, "notes": notes})
        )
        db.add(event)
        db.commit()
        db.refresh(rep)
        
        return {
            "status": "recorded",
            "message": "रिपोर्ट दर्ज हो गई! (Report successfully recorded on Radar)",
            "report_id": rep.id,
            "data": payload
        }
    finally:
        db.close()

@router.get("/radar/alerts")
def get_alerts():
    db = get_session()
    try:
        db_reps = db.exec(select(Report)).all()
        rep_dicts = []
        for r in db_reps:
            try:
                p = json.loads(r.payload)
                rep_dicts.append({
                    "type": r.type,
                    "subtype": p.get("subtype", "blight"),
                    "lat": p.get("lat", 28.615),
                    "lon": p.get("lon", 77.210)
                })
            except Exception:
                pass
        return compute_alerts(rep_dicts)
    finally:
        db.close()

@router.get("/radar/heatmap")
def get_heatmap():
    db = get_session()
    try:
        db_reps = db.exec(select(Report)).all()
        rep_dicts = []
        for r in db_reps:
            try:
                p = json.loads(r.payload)
                rep_dicts.append({
                    "lat": p.get("lat", 28.615),
                    "lon": p.get("lon", 77.210),
                    "weight": 1.0
                })
            except Exception:
                pass
        return compute_heatmap(rep_dicts)
    finally:
        db.close()

@router.post("/doctor/analyze")
def analyze(payload: dict):
    condition = payload.get("condition", "blight").lower()
    conf = float(payload.get("confidence", 0.82))
    
    remedies = REMEDIES_TABLE.get(condition, REMEDIES_TABLE.get("blight", []))
    # Sort remedies cheapest first
    sorted_remedies = sorted(remedies, key=lambda x: x.get("cost_acre", 0))
    
    need_expert = conf < 0.70
    
    cond_names_hi = {
        "blight": "झुलसा रोग (Late Blight)",
        "rust": "गेरुआ / रतुआ (Rust)",
        "khaira": "खैरा रोग (Zinc Deficiency)",
        "leaf_spot": "पत्ती धब्बा रोग (Leaf Spot)"
    }
    
    return {
        "condition": condition,
        "condition_hi": cond_names_hi.get(condition, condition.title()),
        "confidence": conf,
        "confidence_pct": int(round(conf * 100)),
        "expert_advice_needed": need_expert,
        "expert_message": "विशेषज्ञ से पूछो (Confidence below 70% - Consult Krishi Vigyan Kendra)" if need_expert else None,
        "remedies": sorted_remedies,
        "cheapest_remedy": sorted_remedies[0] if sorted_remedies else None,
        "disclaimer": "Sample data / नमूना डेटा - न कि अंतिम कृषि सलाह"
    }
