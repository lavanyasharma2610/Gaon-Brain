import re

NUMBER_WORDS = {"ek":1,"do":2,"teen":3,"char":4,"paanch":5,"cheh":6,"saat":7,"aath":8,"nau":9,"das":10}

def parse_number(text):
    m = re.search(r"(\d+)", text)
    if m: return int(m.group(1))
    for w,n in NUMBER_WORDS.items():
        if w in text: return n
    return None

def parse(text):
    t = text.lower()
    intent = None
    if "becha" in t or "sold" in t: intent = "record_sale"
    elif "bijli on" in t or "power on" in t: intent = "power_on"
    elif "bijli off" in t or "power off" in t: intent = "power_off"
    elif "janwar" in t or "animal" in t: intent = "animal_sighting"
    elif "bimari" in t or "disease" in t: intent = "disease_report"
    return {"intent": intent, "qty": parse_number(t), "raw": text}
EOF