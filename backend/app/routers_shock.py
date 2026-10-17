from fastapi import APIRouter

from app.shock import shock_chain

router = APIRouter()

@router.post("/shock")
def shock(payload: dict):
    return shock_chain(payload.get("type","disease"), payload.get("plot_ids",[]), payload.get("magnitude",1))
