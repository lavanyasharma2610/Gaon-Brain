import re

# Devanagari numeral translation table
DEVA_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

NUMBER_WORDS = {
    # Hinglish / English
    "adha": 0.5, "aadha": 0.5, "paune": 0.75, "ek": 1, "sawa": 1.25,
    "dedh": 1.5, "do": 2, "dhai": 2.5, "teen": 3, "sadhe": 0.5,
    "char": 4, "chaar": 4, "paanch": 5, "panch": 5, "cheh": 6,
    "chhe": 6, "saat": 7, "aath": 8, "ath": 8, "nau": 9, "das": 10,
    "gyarah": 11, "barah": 12, "terah": 13, "chaudah": 14, "pandrah": 15,
    "solah": 16, "satrah": 17, "atharah": 18, "unnis": 19, "bis": 20,
    "bees": 20, "pachis": 25, "pachees": 25, "tees": 30, "paintis": 35,
    "chalis": 40, "pentalis": 45, "pachas": 50, "pachaas": 50,
    "sau": 100, "so": 100, "hazar": 1000, "hazaar": 1000, "lakh": 100000,
    # Hindi Devanagari
    "आधा": 0.5, "पौने": 0.75, "एक": 1, "सवा": 1.25, "डेढ़": 1.5,
    "दो": 2, "ढाई": 2.5, "तीन": 3, "चार": 4, "पांच": 5,
    "पाँच": 5, "छह": 6, "सात": 7, "आठ": 8, "नौ": 9, "दस": 10,
    "ग्यारह": 11, "बारह": 12, "पंद्रह": 15, "बीस": 20, "पच्चीस": 25,
    "तीस": 30, "चालीस": 40, "पचास": 50, "सौ": 100, "हजार": 1000,
    "हज़ार": 1000, "लाख": 100000
}

UNITS = {
    "kilo": 1.0, "kg": 1.0, "kilogram": 1.0, "किलो": 1.0, "किग्रा": 1.0,
    "quintal": 100.0, "quntal": 100.0, "क्विंटल": 100.0, "कुंतल": 100.0,
    "maund": 40.0, "mann": 40.0, "man": 40.0, "मन": 40.0,
    "bori": 50.0, "gatta": 50.0, "बोरी": 50.0, "कट्टा": 50.0, "बोरे": 50.0
}

CROPS_MAP = {
    # Potato / Aalu
    "aalu": ("potato", "आलू"), "aloo": ("potato", "आलू"), "potato": ("potato", "आलू"), "आलू": ("potato", "आलू"),
    # Wheat / Gehun
    "wheat": ("wheat", "गेहूं"), "gehun": ("wheat", "गेहूं"), "gehu": ("wheat", "गेहूं"), "गेहूं": ("wheat", "गेहूं"), "गेहूँ": ("wheat", "गेहूं"),
    # Rice / Dhan
    "rice": ("rice", "धान"), "dhan": ("rice", "धान"), "chawal": ("rice", "चावल"), "धान": ("rice", "धान"), "चावल": ("rice", "चावल"),
    # Mustard / Sarson
    "mustard": ("mustard", "सरसों"), "sarson": ("mustard", "सरसों"), "sarso": ("mustard", "सरसों"), "सरसों": ("mustard", "सरसों"),
    # Gram / Chana
    "chana": ("chana", "चना"), "gram": ("chana", "चना"), "चना": ("chana", "चना"),
    # Tomato / Tamatar
    "tomato": ("tomato", "टमाटर"), "tamatar": ("tomato", "टमाटर"), "टमाटर": ("tomato", "टमाटर"),
    # Onion / Pyaz
    "onion": ("onion", "प्याज"), "pyaz": ("onion", "प्याज"), "pyaaz": ("onion", "प्याज"), "प्याज": ("onion", "प्याज"), "प्याज़": ("onion", "प्याज"),
    # Maize / Makka
    "maize": ("maize", "मक्का"), "makka": ("maize", "मक्का"), "corn": ("maize", "मक्का"), "मक्का": ("maize", "मक्का")
}

BUYERS = [
    "sharma", "gupta", "verma", "patel", "singh", "yadav", "mishra", "kumar",
    "tiwari", "chaudhary", "choudhary", "sharma ji", "gupta ji",
    "शर्मा", "गुप्ता", "वर्मा", "पटेल", "सिंह", "यादव", "मिश्रा", "कुमार", "तिवारी"
]

def normalize_text(text: str) -> str:
    """Normalize text: convert Devanagari numerals to ASCII, lowercase."""
    if not text:
        return ""
    converted = text.translate(DEVA_DIGITS)
    return converted.lower()

def parse_rate(text: str) -> tuple[float | None, str | None, str]:
    """
    Extract rate per kg or per unit, and return (rate, unit, cleaned_text).
    e.g. '10 rupay kilo', '₹20/kg', 'बीस रुपये किलो', 'das rupay kilo', '2000 rupaye quintal'
    """
    norm = normalize_text(text)
    
    # Check digits before rate unit: e.g. 10 rupay kilo
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:rupaye?|rupay|rupe?e?s?|rs|inr|₹|रुपये|रुपए|रुपया)\s*(?:prati|par|per|\/)?\s*(kilo|kg|kilogram|quintal|quntal|maund|किलो|किग्रा|क्विंटल|कुंतल|मन)?", norm)
    if m:
        val = float(m.group(1))
        unit = m.group(2)
        rate_val = val / 100.0 if unit in ["quintal", "quntal", "क्विंटल", "कुंतल"] else val
        cleaned = norm[:m.start()] + " " + norm[m.end():]
        return rate_val, "kg", cleaned

    # Check word numbers before rate unit: e.g. "बीस रुपये किलो", "das rupaye kilo"
    m_words = re.search(r"(\S+)\s+(?:rupaye?|rupay|rupe?e?s?|rs|inr|₹|रुपये|रुपए|रुपया)\s*(?:prati|par|per|\/)?\s*(kilo|kg|kilogram|quintal|quntal|maund|किलो|किग्रा|क्विंटल|कुंतल|मन)?", norm)
    if m_words and m_words.group(1) in NUMBER_WORDS:
        val = float(NUMBER_WORDS[m_words.group(1)])
        unit = m_words.group(2)
        rate_val = val / 100.0 if unit in ["quintal", "quntal", "क्विंटल", "कुंतल"] else val
        cleaned = norm[:m_words.start()] + " " + norm[m_words.end():]
        return rate_val, "kg", cleaned

    # Check "at 25 per kg" or "25/kg" or "25 per kg"
    m_per = re.search(r"(?:at\s+)?(\d+(?:\.\d+)?)\s*(?:per|\/)\s*(kilo|kg|kilogram|quintal|quntal|maund|किलो|किग्रा|क्विंटल|कुंतल|मन)", norm)
    if m_per:
        val = float(m_per.group(1))
        unit = m_per.group(2)
        rate_val = val / 100.0 if unit in ["quintal", "quntal", "क्विंटल", "कुंतल"] else val
        cleaned = norm[:m_per.start()] + " " + norm[m_per.end():]
        return rate_val, "kg", cleaned

    # Pattern: (rate|bhav|भाव|दर) <number>
    m2 = re.search(r"(?:rate|bhav|भाव|दर)\s*(\d+(?:\.\d+)?)", norm)
    if m2:
        val = float(m2.group(1))
        cleaned = norm[:m2.start()] + " " + norm[m2.end():]
        return val, "kg", cleaned

    # Pattern: <number> ka bhav
    m3 = re.search(r"(\d+(?:\.\d+)?)\s*(?:ka\s*bhav|का\s*भाव)", norm)
    if m3:
        val = float(m3.group(1))
        cleaned = norm[:m3.start()] + " " + norm[m3.end():]
        return val, "kg", cleaned

    return None, None, norm

def parse_quantity(text: str, exclude_val: float | None = None) -> tuple[float | None, str | None, float]:
    """
    Extract quantity and unit multiplier.
    Returns (quantity, unit_name, multiplier).
    """
    norm = normalize_text(text)
    
    # Find unit mentioned in text - find the first one that appears
    matched_unit = None
    mult = 1.0
    first_pos = 999999
    
    for u, m in UNITS.items():
        # Match as word or substring
        pos = -1
        match = re.search(rf"\b{re.escape(u)}\b", norm)
        if match:
            pos = match.start()
        elif u in norm and len(u) >= 4:
            pos = norm.find(u)
            
        if pos != -1 and pos < first_pos:
            first_pos = pos
            matched_unit = u
            mult = m

    # Look for number near the unit or general number
    # If unit was found, look for number directly preceding the unit
    if matched_unit:
        m = re.search(rf"(\d+(?:\.\d+)?)\s*{re.escape(matched_unit)}", norm)
        if m:
            val = float(m.group(1))
            return val, matched_unit, mult
        
        # Word numbers before unit e.g. "paanch sau kilo", "dedh quintal", "दो क्विंटल", "सौ किलो"
        prefix_match = re.search(rf"(\S+(?:\s+\S+)?)\s+{re.escape(matched_unit)}", norm)
        if prefix_match:
            cand = prefix_match.group(1).strip()
            words = cand.split()
            if len(words) == 2 and words[0] in NUMBER_WORDS and words[1] in ["sau", "सौ", "hazar", "हजार", "हज़ार"]:
                multiplier_w = 100 if words[1] in ["sau", "सौ"] else 1000
                val = NUMBER_WORDS[words[0]] * multiplier_w
                return float(val), matched_unit, mult
            last_word = words[-1]
            if last_word in NUMBER_WORDS:
                val = NUMBER_WORDS[last_word]
                return float(val), matched_unit, mult
            if words[0] in NUMBER_WORDS:
                val = NUMBER_WORDS[words[0]]
                return float(val), matched_unit, mult


    # Fallback: search for numbers not equal to exclude_val (which is the rate)
    numbers = [float(x) for x in re.findall(r"\b(\d+(?:\.\d+)?)\b", norm)]
    if exclude_val is not None and exclude_val in numbers and len(numbers) > 1:
        numbers.remove(exclude_val)

    if numbers:
        val = numbers[0]
        # Multiplier in text
        if ("sau" in norm or "hundred" in norm or "सौ" in norm) and val < 100:
            val *= 100
        elif ("hazar" in norm or "thousand" in norm or "हजार" in norm or "हज़ार" in norm) and val < 1000:
            val *= 1000
        return val, matched_unit or "kg", mult

    # Check for text numbers (e.g. "paanch sau", "dedh sau", "पचास")
    for w, n in sorted(NUMBER_WORDS.items(), key=lambda x: -len(x[0])):
        if re.search(rf"\b{re.escape(w)}\b", norm):
            val = n
            if ("sau" in norm or "सौ" in norm) and val < 100:
                val *= 100
            elif ("hazar" in norm or "हज़ार" in norm) and val < 1000:
                val *= 1000
            return float(val), matched_unit or "kg", mult

    return None, matched_unit, mult

def parse_crop(text: str) -> tuple[str | None, str | None]:
    """Find crop identifier and Hindi name."""
    norm = normalize_text(text)
    for key, (crop_id, crop_hi) in sorted(CROPS_MAP.items(), key=lambda x: -len(x[0])):
        if re.search(rf"\b{re.escape(key)}\b", norm) or key in norm:
            return crop_id, crop_hi
    return None, None

def parse_buyer(text: str) -> str | None:
    norm = normalize_text(text)
    for b in sorted(BUYERS, key=lambda x: -len(x)):
        if b in norm:
            clean = b.replace(" ji", "").strip()
            return clean
    return None

def parse_intent(text: str) -> str:
    norm = normalize_text(text)
    
    # 1. record_sale
    if any(x in norm for x in ["becha", "bech", "bika", "sold", "sale", "बेचा", "बेची", "बिका", "सेल", "khata", "खाता"]):
        return "record_sale"
    # 2. power_on
    if any(x in norm for x in ["bijli on", "bijli chalu", "bijli aayi", "power on", "बिजली ऑन", "बिजली आई", "बिजली चालू", "लाइट आई"]):
        return "power_on"
    # 3. power_off
    if any(x in norm for x in ["bijli off", "bijli band", "bijli gayi", "power off", "बिजली ऑफ", "बिजली गई", "बिजली बंद", "लाइट गई"]):
        return "power_off"
    # 4. animal_sighting
    if any(x in norm for x in ["janwar", "animal", "kutta", "suvar", "nilgai", "saand", "gaye", "जानवर", "नीलगाय", "सूअर", "सांड", "गाय"]):
        return "animal_sighting"
    # 5. disease_report
    if any(x in norm for x in ["bimari", "disease", "rog", "blight", "khaira", "rust", "keeda", "फफूंद", "बीमारी", "रोग", "कीड़ा", "ब्लाइट"]):
        return "disease_report"
    # 6. tractor_request
    if any(x in norm for x in ["tractor", "ट्रैक्टर", "jutai", "जुताई", "jotne"]):
        return "tractor_request"
    # 7. sowing_plan
    if any(x in norm for x in ["bona", "sowing", "beej", "buwai", "बोना", "बुवाई", "बीज"]):
        return "sowing_plan"
    # 8. irrigation_done
    if any(x in norm for x in ["sinchai", "irrigation", "pani diya", "पानी दिया", "सिंचाई"]):
        return "irrigation_done"
    # 9. loss_report
    if any(x in norm for x in ["nuksan", "loss", "kharab", "barbaad", "नुकसान", "बर्बाद", "खराब"]):
        return "loss_report"
    
    # If crop and quantity or buyer mentioned with numbers, likely a sale
    if parse_crop(text)[0] and ("rupay" in norm or "रुपये" in norm or "kilo" in norm or "किलो" in norm):
        return "record_sale"
        
    return "record_sale"

def parse(text: str) -> dict:
    """
    Parse a spoken or typed sentence in Hindi, Hinglish, or English.
    Returns structured data dictionary.
    """
    intent = parse_intent(text)
    rate, rate_unit, cleaned_text = parse_rate(text)
    qty, unit, mult = parse_quantity(cleaned_text, exclude_val=rate)
    crop, crop_hi = parse_crop(text)
    buyer = parse_buyer(text)

    
    qty_kg = round(qty * mult, 2) if qty is not None else None
    rate_per_kg = round(rate, 2) if rate is not None else None
    
    total = None
    if qty_kg is not None and rate_per_kg is not None:
        total = round(qty_kg * rate_per_kg, 2)
        
    missing = []
    if intent == "record_sale":
        if qty_kg is None:
            missing.append("qty")
        if crop is None:
            missing.append("crop")

    return {
        "intent": intent,
        "qty": qty,
        "unit": unit or "kg",
        "qty_kg": qty_kg,
        "rate": rate_per_kg,
        "total": total,
        "crop": crop,
        "crop_hi": crop_hi,
        "buyer": buyer,
        "missing": missing,
        "raw": text,
    }
