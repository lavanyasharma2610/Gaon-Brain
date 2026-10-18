from datetime import datetime, timedelta

def tractor_schedule(requests: list[dict], tractors_count: int = 3, hours_per_tractor: int = 8) -> dict:
    """
    Fair tractor allocation with multi-tractor daily hour limits and clash handling.
    Fairness criteria:
    1. Fewest prior services first (prev_served_count)
    2. Earliest requested date (want_date)
    """
    if not requests:
        return {
            "schedule": {},
            "peak_demand_unplanned": 0,
            "peak_demand_planned": 0,
            "demand_flattening_pct": 0.0,
            "total_requests": 0,
            "assigned_requests": []
        }

    daily_capacity_hours = tractors_count * hours_per_tractor  # e.g. 24 hours/day
    default_job_hours = 4.0

    # Sort requests fairly: fewest prior services first, then earliest date
    sorted_reqs = sorted(
        requests,
        key=lambda r: (r.get("prev_served_count", 0), r.get("want_date", ""))
    )

    # Calculate uncoordinated peak demand (everyone on their preferred date)
    raw_demand = {}
    for r in requests:
        d = r.get("want_date", "2026-10-20")
        raw_demand[d] = raw_demand.get(d, 0.0) + r.get("hours", default_job_hours)
    peak_unplanned = max(raw_demand.values()) if raw_demand else 0.0

    # Allocate tractors per day, shifting clashes to the next available day
    daily_allocated_hours = {}
    daily_slots = {}
    assigned = []

    for r in sorted_reqs:
        want_date_str = r.get("want_date", "2026-10-20")
        try:
            cur_date = datetime.fromisoformat(want_date_str)
        except Exception:
            cur_date = datetime(2026, 10, 20)

        job_hours = r.get("hours", default_job_hours)
        
        # Find earliest date on or after want_date that has capacity
        while True:
            d_key = cur_date.strftime("%Y-%m-%d")
            used = daily_allocated_hours.get(d_key, 0.0)
            if used + job_hours <= daily_capacity_hours:
                # Assign to this date
                daily_allocated_hours[d_key] = used + job_hours
                tractor_num = int(used // hours_per_tractor) + 1
                
                slot_info = {
                    "request_id": r.get("id"),
                    "farmer_id": r.get("farmer_id"),
                    "farmer_name": r.get("farmer_name", f"किसान {r.get('farmer_id', 1)}"),
                    "original_date": want_date_str,
                    "scheduled_date": d_key,
                    "delayed_days": (cur_date - datetime.fromisoformat(want_date_str)).days if isinstance(want_date_str, str) and len(want_date_str) == 10 else 0,
                    "tractor_id": f"ट्रैक्टर {min(tractor_num, tractors_count)}",
                    "hours": job_hours,
                    "status": "scheduled"
                }
                
                if d_key not in daily_slots:
                    daily_slots[d_key] = []
                daily_slots[d_key].append(slot_info)
                assigned.append(slot_info)
                break
            else:
                # Capacity exceeded for today -> shift to next day
                cur_date += timedelta(days=1)

    peak_planned = max(daily_allocated_hours.values()) if daily_allocated_hours else 0.0
    flattening_pct = round(((peak_unplanned - peak_planned) / max(peak_unplanned, 1.0)) * 100, 1)

    return {
        "schedule": daily_slots,
        "daily_hours": daily_allocated_hours,
        "daily_capacity_hours": daily_capacity_hours,
        "tractors_count": tractors_count,
        "total_requests": len(requests),
        "peak_demand_unplanned": round(peak_unplanned, 1),
        "peak_demand_planned": round(peak_planned, 1),
        "demand_flattening_pct": max(0.0, flattening_pct),
        "assigned_requests": assigned
    }

def bijli_window(power_logs: list[dict], min_days: int = 5) -> dict:
    """
    Find best contiguous 3-hour electricity window from hourly power logs.
    Hourly probability P(on) = on_days / total_days.
    """
    # 24 hours profile
    hourly_stats = {h: {"on_days": 0, "total_days": 0} for h in range(24)}
    
    if power_logs:
        for log in power_logs:
            h = log.get("hour", 0)
            if 0 <= h < 24:
                hourly_stats[h]["on_days"] += log.get("on_days", 0)
                hourly_stats[h]["total_days"] += log.get("total_days", 30)
    else:
        # Realistic fallback synthetic rural feeder profile (peaks around morning 06:00-10:00 and afternoon 14:00-17:00)
        sample_probs = [
            0.15, 0.12, 0.10, 0.10, 0.25, 0.65,
            0.88, 0.92, 0.85, 0.70, 0.40, 0.25,
            0.30, 0.55, 0.82, 0.80, 0.75, 0.50,
            0.35, 0.25, 0.20, 0.18, 0.15, 0.12
        ]
        for h in range(24):
            hourly_stats[h]["on_days"] = int(sample_probs[h] * 30)
            hourly_stats[h]["total_days"] = 30

    hourly_probs = []
    for h in range(24):
        tot = max(hourly_stats[h]["total_days"], 1)
        p = round(hourly_stats[h]["on_days"] / tot, 2)
        hourly_probs.append({
            "hour": h,
            "time_label": f"{h:02d}:00",
            "prob": p,
            "pct": int(p * 100)
        })

    # Find best contiguous 3-hour window
    best_start = 6
    best_avg = -1.0
    for h in range(22):
        avg_p = (hourly_probs[h]["prob"] + hourly_probs[h+1]["prob"] + hourly_probs[h+2]["prob"]) / 3.0
        if avg_p > best_avg:
            best_avg = avg_p
            best_start = h

    window_str = f"{best_start:02d}:00 - {best_start+3:02d}:00"
    
    return {
        "best_window": window_str,
        "start_hour": best_start,
        "end_hour": best_start + 3,
        "average_prob": round(best_avg, 2),
        "average_prob_pct": int(round(best_avg * 100)),
        "hourly_probabilities": hourly_probs,
        "confidence": "Sample data / सिमुलेशन",
        "recommendation_hi": f"श्रेष्ठ बिजली समय: प्रातः {window_str} (उपलब्धता {int(round(best_avg*100))}%)",
        "recommendation_en": f"Optimal power window: {window_str} ({int(round(best_avg*100))}% availability)"
    }

def irrigation_slots(plots: list[dict], budget_hours: float = 18.0, weather_rain_mm: float = 0.0) -> list[dict]:
    """
    Allocate irrigation slots to plots within the best electricity window
    based on crop water interval, days since watering, and plot health.
    """
    # Crop water interval in days
    crop_intervals = {
        "rice": 4, "धान": 4,
        "potato": 7, "आलू": 7,
        "wheat": 14, "गेहूं": 14,
        "chana": 18, "चना": 18,
        "mustard": 21, "सरसों": 21
    }

    results = []
    used_hours = 0.0
    slot_times = ["06:00 - 07:00", "07:00 - 08:00", "08:00 - 09:00"]
    slot_idx = 0

    for idx, p in enumerate(plots):
        c = p.get("crop", "wheat").lower()
        interval = crop_intervals.get(c, 12)
        days_since = p.get("days_since_irrigation", (p.get("id", 1) * 3) % 25)
        health = p.get("health", 1.0)
        
        # Priority score: higher score = greater urgency
        urgency = (days_since / max(interval, 1)) * (2.0 - health)
        
        # Decision logic
        if weather_rain_mm >= 15.0:
            decision = "skip"
            action_hi = "छोड़ दो (Skip)"
            reason_hi = f"अगले 48 घंटों में बारिश ({weather_rain_mm} मिमी) का अनुमान है, पानी की बचत करें"
            reason_en = f"Rain forecast ({weather_rain_mm} mm) in 48h, skip irrigation to save power"
            assigned_slot = "स्थगित (Skipped)"
        elif urgency >= 1.0 and (used_hours + 1.0 <= budget_hours):
            decision = "irrigate"
            action_hi = "सिंचाई करो (Irrigate)"
            assigned_slot = slot_times[slot_idx % len(slot_times)]
            slot_idx += 1
            used_hours += 1.0
            reason_hi = f"{days_since} दिन पहले पानी दिया था (अंतराल {interval} दिन); तुरंत सिंचाई स्लॉट आवंटित"
            reason_en = f"Last irrigated {days_since} days ago (interval {interval}d); urgent slot allocated"
        elif urgency >= 0.7:
            decision = "wait"
            action_hi = "इंतजार करो (Wait)"
            assigned_slot = "कल का स्लॉट (Tomorrow)"
            reason_hi = f"नमी पर्याप्त है; कल के बिजली स्लॉट में पानी दें"
            reason_en = f"Soil moisture adequate; schedule for tomorrow's power window"
        else:
            decision = "skip"
            action_hi = "छोड़ दो (No need)"
            assigned_slot = "आवश्यकता नहीं (Not needed)"
            reason_hi = f"फसल हरी और स्वस्थ है ({days_since}/{interval} दिन)"
            reason_en = f"Crop healthy and well-watered ({days_since}/{interval} days)"

        results.append({
            "plot_id": p.get("id"),
            "farmer_name": p.get("farmer_name", f"किसान {p.get('farmer_id', idx+1)}"),
            "crop": c,
            "crop_hi": "आलू" if "potato" in c or "aalu" in c else ("गेहूं" if "wheat" in c else ("धान" if "rice" in c else "सरसों")),
            "area_acre": p.get("area_acre", 1.5),
            "days_since": days_since,
            "crop_interval": interval,
            "urgency_score": round(urgency, 2),
            "decision": decision,
            "action_hi": action_hi,
            "slot_time": assigned_slot,
            "reason_hi": reason_hi,
            "reason_en": reason_en,
            "feeder_id": p.get("feeder_id", 1)
        })

    return results
