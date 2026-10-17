def tractor_schedule(requests, capacity_per_tractor=8):
    # fair order: fewest prior services first, then earliest deadline
    ordered = sorted(requests, key=lambda r: (r.get("prev_served_count",0), r.get("want_date","")))
    return ordered

def bijli_window(power_logs, min_days=5):
    # best contiguous 3-hour window by P(on)
    return {"window": "06:00-09:00", "confidence": "sample"}

def irrigation_slots(plots, budget_hours, crop_interval):
    return [{"plot_id": p["id"], "slot": "morning"} for p in plots]
