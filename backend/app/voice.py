import re
INTENTS = ["record_sale","power_on","power_off","animal_sighting","disease_report","tractor_request","sowing_plan","irrigation_done","loss_report"]
def parse(text):
    t = text.lower()
    intent = "record_sale" if "becha" in t or "sold" in t else None
    return {"intent": intent, "raw": text}
EOF