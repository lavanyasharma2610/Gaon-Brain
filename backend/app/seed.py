import random
from datetime import datetime, timedelta
from app.db import engine, get_session
from app.models import *
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
    for f in farmers: s.refresh(f)
    crops = ["wheat","rice","mustard","chana"]
    plots = []
    for i in range(30):
        f = random.choice(farmers)
        p = Plot(farmer_id=f.id, area_acre=round(random.uniform(0.5,3.0),2),
                 crop=random.choice(crops), polygon="[]", expected_yield=round(random.uniform(8,20),2))
        s.add(p); plots.append(p)
    s.commit()
    for p in plots: s.refresh(p)
    buyers = []
    for i in range(6):
        b = Buyer(name=f"Buyer {i+1}"); s.add(b); buyers.append(b)
    s.commit()
    for b in buyers: s.refresh(b)
    lots = []
    for i in range(5):
        l = Lot(crop=random.choice(crops), week=random.randint(0,4), expected_qty=round(random.uniform(100,500),2))
        s.add(l); lots.append(l)
    s.commit()
    for l in lots: s.refresh(l)
    for l in lots:
        c = Commitment(lot_id=l.id, buyer_id=random.choice(buyers).id, qty=round(random.uniform(10,100),2))
        s.add(c)
    s.commit()
    tractors = []
    for i in range(3):
        pass
    for i in range(8):
        tr = TractorRequest(farmer_id=random.choice(farmers).id, want_date=(datetime.utcnow()+timedelta(days=random.randint(0,10))).date().isoformat(), prev_served_count=random.randint(0,3))
        s.add(tr)
    s.commit()
    feeders = [1,2]
    for fid in feeders:
        for h in range(24):
            pl = PowerLog(feeder_id=fid, hour=h, on_days=random.randint(0,30), total_days=30)
            s.add(pl)
    s.commit()
    for p in plots:
        ws = WaterSlot(plot_id=p.id, slot="morning")
        s.add(ws)
    s.commit()
    plan = Plan(name="season1"); s.add(plan); s.commit(); s.refresh(plan)
    for p in plots:
        pi = PlanItem(plan_id=plan.id, plot_id=p.id, crop=p.crop, week=0)
        s.add(pi)
    s.commit()
    for i in range(5):
        pur = Purchase(farmer_id=random.choice(farmers).id, product="urea", mrp=500, paid=random.choice([480,520,500]), bill_received=random.choice([True,False]))
        s.add(pur)
    s.commit()
    cons = Consent(farmer_id=farmers[0].id, code="1234", expires_at=datetime.utcnow()+timedelta(hours=24))
    s.add(cons); s.commit()
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