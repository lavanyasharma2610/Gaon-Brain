import csv, os

class PriceProvider:
    def __init__(self, path="data/mandi.csv"):
        self.path = path
    def modal_price(self, crop):
        if not os.path.exists(self.path):
            return None
        prices = []
        with open(self.path) as f:
            for row in csv.DictReader(f):
                if row.get("crop")==crop:
                    try: prices.append(float(row["price"]))
                    except: pass
        return sum(prices)/len(prices) if prices else None

class WeatherProvider:
    def forecast(self):
        return {"rain_mm_48h": 0, "prob": 0.2}

class DiseaseProvider:
    def analyze(self, condition, confidence):
        return {"condition": condition, "confidence": confidence}
EOF