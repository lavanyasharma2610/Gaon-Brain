import json
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from sqlmodel import select

from app.db import get_session
from app.models import Event, Farmer, Sale
from app.voice import parse

router = APIRouter()
sessions = {}

class ParseIn(BaseModel):
    text: str
    farmer_id: int | None = 1

class ConfirmIn(BaseModel):
    session_id: str
    answer: str

@router.post("/voice/parse")
def voice_parse(inp: ParseIn):
    r = parse(inp.text)
    sid = f"s{len(sessions)+1}"
    sessions[sid] = {**r, "farmer_id": inp.farmer_id or 1}
    
    if r["missing"]:
        field_hi = "मात्रा (किलो)" if r["missing"][0] == "qty" else "फसल का नाम"
        return {
            "session_id": sid,
            "status": "need_field",
            "field": r["missing"][0],
            "message": f"कृपया {field_hi} बताएं",
            "parsed": r
        }
    return {
        "session_id": sid,
        "status": "confirm",
        "message": "क्या यह सही है? (हाँ / नहीं)",
        "parsed": r
    }

@router.post("/voice/confirm")
def voice_confirm(inp: ConfirmIn):
    sess = sessions.get(inp.session_id)
    if not sess:
        return {"status": "not_found", "message": "सत्र नहीं मिला"}
    
    ans = inp.answer.strip().lower()
    positive = {"haan", "yes", "ha", "haanji", "sahi hai", "sahi", "हाँ", "हा", "हाँजी", "सही है"}
    negative = {"nahi", "no", "na", "galat", "नहीं", "ना", "गलत"}
    
    if ans in positive:
        qty_kg = sess.get("qty_kg") or 0.0
        rate = sess.get("rate") or 0.0
        total = sess.get("total") or round(qty_kg * rate, 2)
        sess["total"] = total
        farmer_id = sess.get("farmer_id", 1)
        
        # Save to database
        db = get_session()
        try:
            # Create Sale if intent is record_sale
            if sess.get("intent") == "record_sale" and qty_kg > 0:
                sale = Sale(
                    farmer_id=farmer_id,
                    qty_kg=qty_kg,
                    rate=rate,
                    ts=datetime.now(timezone.utc)
                )
                db.add(sale)
                db.commit()
                db.refresh(sale)
                sess["sale_id"] = sale.id
            
            # Create Event
            event = Event(
                type=sess.get("intent", "record_sale"),
                farmer_id=farmer_id,
                payload=json.dumps(sess, default=str),
                raw_text=sess.get("raw", ""),
                ts=datetime.now(timezone.utc)
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            sess["event_id"] = event.id
            
            # Fetch farmer name
            farmer = db.get(Farmer, farmer_id)
            farmer_name = farmer.name if farmer else f"किसान {farmer_id}"
            sess["farmer_name"] = farmer_name
            
            # Total logbook count
            count = len(db.exec(select(Event)).all())
        finally:
            db.close()
            
        return {
            "status": "saved",
            "message": "खाते में दर्ज हो गया! (Recorded in Village Ledger)",
            "data": sess,
            "logbook_count": count
        }
        
    if ans in negative:
        return {"status": "cancelled", "message": "रद्द कर दिया गया (Cancelled)"}
        
    return {"status": "ask", "message": "कृपया हाँ या नहीं कहें (Say Haan or Nahi)"}
