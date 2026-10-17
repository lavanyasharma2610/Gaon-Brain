import re

NUMBER_WORDS = {"ek":1,"do":2,"teen":3,"char":4,"paanch":5,"cheh":6,"saat":7,"aath":8,"nau":9,"das":10,"gyarah":11,"barah":12,"pandrah":15,"bis":20,"pachis":25,"tees":30,"pachas":50,"sau":100,"hazar":1000,"dedh":1.5,"sadhe":1.5,"paune":0.75}

UNITS = {"kilo":1,"kg":1,"kilogram":1,"quintal":100,"maund":40}

CROPS = ["wheat","rice","mustard","chana","gehun","dhan","sarson"]

BUYERS = ["sharma","gupta","verma","patel"]

def parse_number(text):
    # handle "paanch sau", "dedh sau", "sadhe teen"
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    if m:
        val = float(m.group(1))
        # unit multiplier
        if "sau" in text or "hundred" in text:
            val *= 100
        if "hazar" in text or "thousand" in text:
            val *= 1000
        return val
    for w,n in NUMBER_WORDS.items():
        if w in text:
            base = n
            if "sau" in text:
                base *= 100
            if "hazar" in text:
                base *= 1000
            return base
    return None

def parse_unit(text):
    for u,m in UNITS.items():
        if u in text:
            return u, m
    return None, 1

def parse_crop(text):
    for c in CROPS:
        if c in text:
            return c
    # fuzzy-ish
    if "gehu" in text or "gehun" in text:
        return "wheat"
    if "dhan" in text or "chawal" in text:
        return "rice"
    return None

def parse_buyer(text):
    for b in BUYERS:
        if b in text:
            return b
    return None

def parse_intent(text):
    t = text.lower()
    if any(x in t for x in ["becha","bech","sold","sale"]):
        return "record_sale"
    if "bijli on" in t or "bijli chalu" in t or "power on" in t:
        return "power_on"
    if "bijli off" in t or "bijli band" in t or "power off" in t:
        return "power_off"
    if any(x in t for x in ["janwar","animal","kutta","suvar","nilgai"]):
        return "animal_sighting"
    if any(x in t for x in ["bimari","disease","rog","blight","khaira"]):
        return "disease_report"
    if "tractor" in t:
        return "tractor_request"
    if any(x in t for x in ["bona","sowing","beej"]):
        return "sowing_plan"
    if any(x in t for x in ["sinchai","irrigation","pani"]):
        return "irrigation_done"
    if any(x in t for x in ["nuksan","loss","kharab"]):
        return "loss_report"
    return None

def parse(text):
    intent = parse_intent(text)
    qty = parse_number(text)
    unit, mult = parse_unit(text)
    crop = parse_crop(text)
    buyer = parse_buyer(text)
    qty_kg = (qty * mult) if qty is not None else None
    missing = []
    if intent == "record_sale":
        if qty_kg is None: missing.append("qty")
        if crop is None: missing.append("crop")
    return {
        "intent": intent,
        "qty": qty,
        "unit": unit,
        "qty_kg": qty_kg,
        "crop": crop,
        "buyer": buyer,
        "missing": missing,
        "raw": text,
    }
