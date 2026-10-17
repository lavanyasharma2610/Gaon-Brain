from fastapi import APIRouter
from sqlmodel import select

from app.db import get_session
from app.models import Event

router = APIRouter()

@router.get("/logbook")
def logbook():
    s = get_session()
    return s.exec(select(Event)).all()
