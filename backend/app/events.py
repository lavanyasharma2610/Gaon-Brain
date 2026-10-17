import json

from sqlmodel import Session

from app.models import Event


def append_event(session: Session, type: str, **kw) -> Event:
    payload = kw.pop("payload", {})
    ev = Event(type=type, payload=json.dumps(payload), **kw)
    session.add(ev)
    session.commit()
    session.refresh(ev)
    return ev
