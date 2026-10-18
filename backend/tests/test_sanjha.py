from app.sanjha import bijli_window, irrigation_slots, tractor_schedule

def test_tractor_fair():
    reqs = [
        {"id": 1, "prev_served_count": 2, "want_date": "2026-10-20", "hours": 4.0},
        {"id": 2, "prev_served_count": 0, "want_date": "2026-10-20", "hours": 4.0}
    ]
    res = tractor_schedule(reqs, tractors_count=3, hours_per_tractor=8)
    assigned = res["assigned_requests"]
    assert assigned[0]["request_id"] == 2
    assert assigned[1]["request_id"] == 1

def test_bijli_window_calculation():
    # Feeder with peak power in hours 6, 7, 8
    power_logs = [
        {"hour": 6, "on_days": 28, "total_days": 30},
        {"hour": 7, "on_days": 29, "total_days": 30},
        {"hour": 8, "on_days": 27, "total_days": 30},
        {"hour": 14, "on_days": 10, "total_days": 30}
    ]
    res = bijli_window(power_logs)
    assert res["best_window"] == "06:00 - 09:00"
    assert res["average_prob"] > 0.85
    assert len(res["hourly_probabilities"]) == 24

def test_irrigation_slots_priority():
    plots = [
        {"id": 1, "crop": "rice", "days_since_irrigation": 5, "health": 0.8},
        {"id": 2, "crop": "mustard", "days_since_irrigation": 2, "health": 1.0}
    ]
    res = irrigation_slots(plots, budget_hours=10.0, weather_rain_mm=0.0)
    assert len(res) == 2
    # Rice with days_since > interval gets irrigate decision
    assert res[0]["decision"] == "irrigate"
    # Mustard recently watered gets skip/wait
    assert res[1]["decision"] in ["wait", "skip"]

def test_irrigation_skip_on_rain():
    plots = [{"id": 1, "crop": "rice", "days_since_irrigation": 6, "health": 0.8}]
    res = irrigation_slots(plots, budget_hours=10.0, weather_rain_mm=25.0)
    assert res[0]["decision"] == "skip"
    assert "बारिश" in res[0]["reason_hi"]
