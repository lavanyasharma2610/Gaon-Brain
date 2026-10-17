from fastapi import APIRouter
from app.bazaar import build_lots, buyer_trust

router = APIRouter()

@router.get("/bazaar/lots")
def lots():
    return build_lots([])

@router.post("/bazaar/commit")
def commit(payload: dict):
    return {"status": "committed", "data": payload}

@router.get("/bazaar/payments")
def payments():
    return []

@router.get("/bazaar/buyers")
def buyers():
    return []
EOF