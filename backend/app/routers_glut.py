from fastapi import APIRouter
from app.glut import plan

router = APIRouter()

@router.get("/glut/state")
def state():
    return {"status": "ok"}

@router.post("/glut/plan")
def glut_plan(payload: dict):
    return plan(payload.get("plots",[]), payload.get("crop_params",{}))
EOF