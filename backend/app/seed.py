import random
from datetime import datetime, timedelta
from app.db import engine, get_session
from app.models import Village, Farmer, Plot, Event
from sqlmodel import SQLModel

def seed():
    SQLModel.metadata.create_all(engine)
    s = get_session()
    v = Village(name="Fictional Gaon")
    s.add(v); s.commit(); s.refresh(v)
    farmers = []
    for i in range(24):
        f = Farmer(village_id=v.id, name=f"Kisan {i+1}")
        s.add(f); farmers.append(f)
    s.commit()
    for f in farmers:
        s.refresh(f)
    crops = ["wheat","rice","mustard","chana"]
    plots = []
    for i in range(30):
        f = random.choice(farmers)
        p = Plot(farmer_id=f.id, area_acre=round(random.uniform(0.5,3.0),2),
                 crop=random.choice(crops), polygon="[]", expected_yield=round(random.uniform(8,20),2))
        s.add(p); plots.append(p)
    s.commit()
    for p in plots:
        s.refresh(p)
    # synthetic mandi csv
    with open("data/mandi.csv","w") as fh:
        fh.write("# SYNTHETIC DATA\n")
        fh.write("date,crop,price\n")
        for d in range(60):
            dt = (datetime.utcnow()-timedelta(days=d)).date()
            for c in crops:
                fh.write(f"{dt},{c},{round(random.uniform(1800,3200),2)}\n")
    print("seeded")

if __name__ == "__main__":
    seed()
EOF