from fastapi import APIRouter
from app.shock import shock_chain

router = APIRouter()

@router.get("/shock")
@router.post("/shock")
def shock(payload: dict | None = None):
    payload = payload or {}
    stype = payload.get("type", "disease")
    plots = payload.get("plot_ids") or [1, 2, 3]
    mag = payload.get("magnitude", 1.0)
    return shock_chain(shock_type=stype, plot_ids=plots, magnitude=mag)
