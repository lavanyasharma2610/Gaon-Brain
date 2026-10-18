from fastapi import APIRouter
from app.sim import simulate_adoption_sweep, simulate_cobweb, simulate_shock

router = APIRouter()

@router.post("/sim/cobweb")
@router.get("/sim/cobweb")
def sim_cobweb(payload: dict | None = None):
    payload = payload or {}
    seasons = payload.get("seasons", 6)
    crop = payload.get("crop", "potato")
    k = payload.get("K", 0.08)
    return simulate_cobweb(seasons=seasons, crop=crop, K=k)

@router.post("/sim/adoption")
@router.get("/sim/adoption")
def sim_adoption(payload: dict | None = None):
    payload = payload or {}
    plots = payload.get("plots_count", 30)
    area = payload.get("total_area", 60.0)
    return simulate_adoption_sweep(plots_count=plots, total_area=area)

@router.post("/sim/shock")
def sim_shock(payload: dict | None = None):
    payload = payload or {}
    stype = payload.get("shock_type", payload.get("type", "disease"))
    mag = payload.get("magnitude", 0.35)
    return simulate_shock(shock_type=stype, magnitude=mag)
