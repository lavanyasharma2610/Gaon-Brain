from fastapi import APIRouter
from app.db import get_session
from app.models import Event
from sqlmodel import select

router = APIRouter()

@router.get("/logbook")
def logbook():
    s = get_session()
    return s.exec(select(Event)).all()
EOF