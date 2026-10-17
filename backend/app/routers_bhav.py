from fastapi import APIRouter

from app.providers import PriceProvider

router = APIRouter()
pp = PriceProvider()

@router.get("/bhav/tulna")
def bhav_tulna(crop: str, sold_rate: float):
    modal = pp.modal_price(crop)
    diff = (sold_rate - modal) if modal else None
    return {"crop": crop, "sold_rate": sold_rate, "modal": modal, "diff": diff}
