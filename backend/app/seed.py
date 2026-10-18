import json
import os
import random
from datetime import datetime, timedelta, timezone

from sqlmodel import SQLModel

from app.db import DB_PATH, engine, get_session
from app.models import (
    Buyer,
    Commitment,
    Consent,
    Event,
    Farmer,
    Lot,
    Plan,
    PlanItem,
    Plot,
    PowerLog,
    Purchase,
    Report,
    Sale,
    TractorRequest,
    Village,
    WaterSlot,
)

def seed():
    # Fresh recreate
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    s = get_session()
    v = Village(name="शिवपुर (Fictional Gaon)")
    s.add(v)
    s.commit()
    s.refresh(v)
    
    # 24 Farmers with authentic village names
    farmer_names = [
        "राम कुमार", "श्याम सुंदर", "हरि प्रसाद", "सुरेश यादव", "रमेश सिंह",
        "दिनेश शर्मा", "राजेश पटेल", "मुकेश वर्मा", "अनिल मिश्रा", "सुनील चौधरी",
        "कमलेश तिवारी", "जगदीश चौहान", "बीरबल यादव", "फूलचंद", "दीनानाथ",
        "प्रताप सिंह", "रतन लाल", "काशीराम", "भगवान दास", "संतोष कुमार",
        "उमेश सिंह", "गोपाल दास", "महेश चंद्र", "किशन लाल"
    ]
    farmers = []
    for i, name in enumerate(farmer_names):
        f = Farmer(village_id=v.id, name=name, role="farmer")
        s.add(f)
        farmers.append(f)
    s.commit()
    for f in farmers:
        s.refresh(f)
        
    crops = ["wheat", "rice", "mustard", "chana", "potato"]
    
    # Generate 30 plots with 6 cols x 5 rows SVG layout
    cols = 6
    pw = 85
    ph = 60
    pad_x = 20
    pad_y = 25
    gap_x = 10
    gap_y = 12
    
    plots = []
    random.seed(42)  # Deterministic seed for reproducible demo
    
    for i in range(30):
        r = i // cols
        c = i % cols
        x = pad_x + c * (pw + gap_x)
        y = pad_y + r * (ph + gap_y)
        poly = [[x, y], [x + pw, y], [x + pw, y + ph], [x, y + ph]]
        
        f = farmers[i % len(farmers)]
        crop = crops[i % len(crops)]
        feeder = 1 if r < 3 else 2
        
        p = Plot(
            farmer_id=f.id,
            area_acre=round(random.uniform(1.0, 2.5), 1),
            crop=crop,
            health=1.0,
            expected_yield=round(random.uniform(1200, 2400) if crop != "potato" else random.uniform(6000, 9000), 1),
            polygon=json.dumps(poly),
            feeder_id=feeder
        )
        s.add(p)
        plots.append(p)
    s.commit()
    for p in plots:
        s.refresh(p)
        
    # Buyers
    buyer_names = ["शर्मा ट्रेडर्स", "गुप्ता एग्रो", "वर्मा जी मंडी", "पटेल ब्रदर्स", "किसान सेवा केंद्र", "चौधरी ट्रेडिंग"]
    buyers = []
    for name in buyer_names:
        b = Buyer(name=name)
        s.add(b)
        buyers.append(b)
    s.commit()
    for b in buyers:
        s.refresh(b)
        
    # Bulk lots
    lots = []
    for i in range(5):
        l = Lot(crop=crops[i], week=i % 4, expected_qty=round(random.uniform(150, 450), 1))
        s.add(l)
        lots.append(l)
    s.commit()
    for l in lots:
        s.refresh(l)
        c = Commitment(lot_id=l.id, buyer_id=buyers[l.id % len(buyers)].id, qty=round(random.uniform(50, 120), 1))
        s.add(c)
    s.commit()
    
    # Tractor Requests
    now = datetime.now(timezone.utc)
    for i in range(8):
        req_date = (now + timedelta(days=i // 2)).date().isoformat()
        tr = TractorRequest(
            farmer_id=farmers[i % len(farmers)].id,
            want_date=req_date,
            prev_served_count=i % 3
        )
        s.add(tr)
    s.commit()
    
    # Power logs for 2 feeders
    sample_probs = [
        0.15, 0.12, 0.10, 0.10, 0.25, 0.65,
        0.88, 0.92, 0.85, 0.70, 0.40, 0.25,
        0.30, 0.55, 0.82, 0.80, 0.75, 0.50,
        0.35, 0.25, 0.20, 0.18, 0.15, 0.12
    ]
    for fid in [1, 2]:
        for h in range(24):
            mult = 1.0 if fid == 1 else 0.9
            on_d = int(sample_probs[h] * 30 * mult)
            pl = PowerLog(feeder_id=fid, hour=h, on_days=on_d, total_days=30)
            s.add(pl)
    s.commit()
    
    # Water slots
    slot_names = ["06:00 - 07:00", "07:00 - 08:00", "08:00 - 09:00"]
    for i, p in enumerate(plots):
        ws = WaterSlot(plot_id=p.id, slot=slot_names[i % len(slot_names)])
        s.add(ws)
    s.commit()
    
    # Initial Plan
    plan_obj = Plan(name="प्रारंभिक बुवाई योजना (Initial Sowing Season)")
    s.add(plan_obj)
    s.commit()
    s.refresh(plan_obj)
    
    for p in plots:
        pi = PlanItem(plan_id=plan_obj.id, plot_id=p.id, crop=p.crop, week=0)
        s.add(pi)
    s.commit()
    
    # Initial Sales & Events for Logbook
    sales_seed = [
        {"farmer": farmers[0], "crop": "potato", "crop_hi": "आलू", "qty": 500.0, "rate": 10.0, "buyer": "शर्मा जी", "text": "500 kilo aalu, 10 rupay kilo, Sharma ji ko"},
        {"farmer": farmers[1], "crop": "wheat", "crop_hi": "गेहूं", "qty": 200.0, "rate": 22.0, "buyer": "गुप्ता एग्रो", "text": "2 quintal gehu becha 2200 rupaye quintal"},
        {"farmer": farmers[2], "crop": "mustard", "crop_hi": "सरसों", "qty": 80.0, "rate": 52.0, "buyer": "वर्मा जी", "text": "80 kilo sarson becha 52 rupay kilo Verma ji ko"},
        {"farmer": farmers[3], "crop": "chana", "crop_hi": "चना", "qty": 150.0, "rate": 48.0, "buyer": "पटेल ब्रदर्स", "text": "150 kilo chana becha 48 rupay kilo Patel ko"}
    ]
    for ss in sales_seed:
        sale = Sale(
            farmer_id=ss["farmer"].id,
            qty_kg=ss["qty"],
            rate=ss["rate"],
            ts=now - timedelta(days=random.randint(1, 5))
        )
        s.add(sale)
        
        ev = Event(
            type="record_sale",
            farmer_id=ss["farmer"].id,
            raw_text=ss["text"],
            payload=json.dumps({
                "crop": ss["crop"],
                "crop_hi": ss["crop_hi"],
                "qty_kg": ss["qty"],
                "rate": ss["rate"],
                "total": round(ss["qty"] * ss["rate"], 2),
                "buyer": ss["buyer"]
            }),
            ts=sale.ts
        )
        s.add(ev)
    s.commit()
    
    # Initial Radar Reports
    reports_seed = [
        {"type": "disease", "subtype": "blight", "notes": "पत्तियों पर भूरे धब्बे दिखे", "lat": 28.615, "lon": 77.210},
        {"type": "disease", "subtype": "blight", "notes": "आलू में झुलसा रोग की शुरुआत", "lat": 28.616, "lon": 77.211},
        {"type": "disease", "subtype": "blight", "notes": "खेत 3 में भी लक्षण", "lat": 28.617, "lon": 77.212},
        {"type": "animal", "subtype": "nilgai", "notes": "नहर के पास 3 नीलगाय दिखीं", "lat": 28.622, "lon": 77.218}
    ]
    for rs in reports_seed:
        rep = Report(
            type=rs["type"],
            payload=json.dumps({
                "subtype": rs["subtype"],
                "notes": rs["notes"],
                "lat": rs["lat"],
                "lon": rs["lon"],
                "ts": (now - timedelta(hours=random.randint(2, 48))).isoformat()
            })
        )
        s.add(rep)
    s.commit()
    
    # Synthetic Mandi Prices CSV
    data_dir = os.path.dirname(DB_PATH)
    os.makedirs(data_dir, exist_ok=True)
    mandi_csv_path = os.path.join(data_dir, "mandi.csv")
    
    with open(mandi_csv_path, "w", encoding="utf-8") as fh:
        fh.write("# SYNTHETIC DATA - Sample Mandi Prices\n")
        fh.write("date,crop,price\n")
        for d in range(60):
            dt = (now - timedelta(days=d)).date().isoformat()
            for c in crops:
                base_p = {"wheat": 2200, "rice": 2100, "mustard": 5200, "chana": 4800, "potato": 1200}[c]
                price = round(base_p * random.uniform(0.92, 1.08), 1)
                fh.write(f"{dt},{c},{price}\n")

    print(f"Database seeded successfully at {DB_PATH} with 30 polygon plots, 24 farmers, and sample data.")

if __name__ == "__main__":
    seed()
