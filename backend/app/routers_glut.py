from fastapi import APIRouter
from sqlmodel import select

from app.db import get_session
from app.glut import DEFAULT_CROP_PARAMS, plan
from app.models import Farmer, Plan, PlanItem, Plot

router = APIRouter()

def _fetch_db_plots():
    db = get_session()
    try:
        plots = db.exec(select(Plot)).all()
        farmers = {f.id: f.name for f in db.exec(select(Farmer)).all()}
        
        plot_list = []
        for p in plots:
            plot_list.append({
                "id": p.id,
                "farmer_id": p.farmer_id,
                "farmer_name": farmers.get(p.farmer_id, f"किसान {p.farmer_id}"),
                "area_acre": p.area_acre,
                "crop": p.crop,
                "health": p.health,
                "expected_yield": p.expected_yield,
                "polygon": p.polygon,
                "feeder_id": p.feeder_id
            })
        return plot_list
    finally:
        db.close()

@router.get("/glut/state")
def glut_state():
    """Return village current plots, baseline state, and default parameters."""
    plots = _fetch_db_plots()
    res = plan(plots, DEFAULT_CROP_PARAMS)
    return {
        "status": "ok",
        "plots_count": len(plots),
        "crop_params": DEFAULT_CROP_PARAMS,
        "current_plan": res,
        "is_applied": False
    }

@router.post("/glut/plan")
def glut_plan(payload: dict | None = None):
    """Run Glut Guard optimization on given or seeded village plots."""
    payload = payload or {}
    plots = payload.get("plots")
    if not plots:
        plots = _fetch_db_plots()
    crop_params = payload.get("crop_params") or DEFAULT_CROP_PARAMS
    k = payload.get("K", 0.05)
    return plan(plots, crop_params, K=k)

@router.post("/glut/apply")
def glut_apply(payload: dict | None = None):
    """Apply plan to village: persist to Plan and PlanItem database tables."""
    payload = payload or {}
    plots = payload.get("plots")
    if not plots:
        plots = _fetch_db_plots()
    crop_params = payload.get("crop_params") or DEFAULT_CROP_PARAMS
    k = payload.get("K", 0.05)
    
    result = plan(plots, crop_params, K=k)
    
    db = get_session()
    try:
        new_plan = Plan(name="Glut Guard Optimal Sowing Season 2026")
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
        
        for p in plots:
            pid = p["id"]
            asgn = result["assignment"].get(pid, {})
            pi = PlanItem(
                plan_id=new_plan.id,
                plot_id=pid,
                crop=asgn.get("crop", p.get("crop", "wheat")),
                week=asgn.get("week", 0)
            )
            db.add(pi)
            
            # Update plot in DB
            db_plot = db.get(Plot, pid)
            if db_plot and asgn.get("crop"):
                db_plot.crop = asgn["crop"]
                db.add(db_plot)
                
        db.commit()
        plan_id = new_plan.id
    finally:
        db.close()
        
    return {
        "applied": True,
        "message": "गाँव योजना सफलतापूर्वक लागू हो गई (Village Plan Applied)",
        "plan_id": plan_id,
        "plan": result
    }
