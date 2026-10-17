import tempfile

from fastapi import APIRouter, Response

from app.claim_pdf import generate_claim_kit_pdf
from app.suraksha import claim_kit, kharid_check, sinchai_card

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

@router.post("/suraksha/claim/pdf")
def claim_pdf(payload: dict):
    # Build full dossier data from payload
    dossier = {
        "farmer": payload.get("farmer", ""),
        "policy_no": payload.get("policy_no", ""),
        "survey_no": payload.get("survey_no", ""),
        "crop": payload.get("crop", ""),
        "area": payload.get("area", 0),
        "event_type": payload.get("event_type", ""),
        "event_at": payload.get("event_at", ""),
        "policy_status": payload.get("policy_status", "unknown"),
        "sowing_record": payload.get("sowing_record", {}),
        "photos": payload.get("photos", []),
        "weather_snapshot": payload.get("weather_snapshot", {}),
        "purchases": payload.get("purchases", []),
        "dossier_hash": payload.get("dossier_hash", ""),
    }
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    generate_claim_kit_pdf(dossier, path)
    with open(path, "rb") as f:
        pdf_bytes = f.read()
    import os
    os.unlink(path)
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=claim_kit.pdf"})
