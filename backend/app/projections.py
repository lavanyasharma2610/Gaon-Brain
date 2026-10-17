from sqlmodel import Session, select
from app.models import Plot, Event

def recompute_plot_health(session: Session, plot_id: int) -> float:
    events = session.exec(select(Event).where(Event.plot_id==plot_id)).all()
    health = 1.0
    for e in events:
        if e.type == "disease_report":
            health -= 0.2
    return max(0.0, health)
EOF