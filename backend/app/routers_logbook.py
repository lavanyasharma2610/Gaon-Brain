import json
from fastapi import APIRouter
from sqlmodel import select

from app.db import get_session
from app.models import Event, Farmer

router = APIRouter()

@router.get("/logbook")
def logbook():
    db = get_session()
    try:
        events = db.exec(select(Event).order_by(Event.ts.desc())).all()
        farmers = {f.id: f.name for f in db.exec(select(Farmer)).all()}
        
        results = []
        for e in events:
            payload = {}
            if e.payload:
                try:
                    payload = json.loads(e.payload)
                except Exception:
                    payload = {}
                    
            farmer_name = farmers.get(e.farmer_id, f"किसान {e.farmer_id or 1}")
            crop = payload.get("crop", "अज्ञात")
            crop_hi = payload.get("crop_hi", crop)
            qty_kg = payload.get("qty_kg")
            rate = payload.get("rate")
            total = payload.get("total")
            buyer = payload.get("buyer")
            
            ts_str = e.ts.strftime("%d-%m-%Y %H:%M") if hasattr(e.ts, "strftime") else str(e.ts)[:16]
            
            results.append({
                "id": e.id,
                "type": e.type,
                "farmer_id": e.farmer_id,
                "farmer_name": farmer_name,
                "crop": crop,
                "crop_hi": crop_hi,
                "qty_kg": qty_kg,
                "rate": rate,
                "total": total,
                "buyer": buyer,
                "raw_text": e.raw_text,
                "timestamp": ts_str,
                "payload": payload
            })
        return results
    finally:
        db.close()
