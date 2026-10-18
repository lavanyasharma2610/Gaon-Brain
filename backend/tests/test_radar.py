from app.radar import compute_alerts, compute_heatmap, haversine

def test_haversine():
    d = haversine(0, 0, 0, 0)
    assert d == 0
    # Delhi to nearby point (~1.1 km)
    d2 = haversine(28.61, 77.20, 28.62, 77.20)
    assert 1.0 < d2 < 1.3

def test_radar_alerts_cluster():
    reports = [
        {"type": "disease", "subtype": "blight", "lat": 28.615, "lon": 77.210},
        {"type": "disease", "subtype": "blight", "lat": 28.616, "lon": 77.211},
        {"type": "disease", "subtype": "blight", "lat": 28.617, "lon": 77.212}
    ]
    alerts = compute_alerts(reports, N=3, R_km=2.0)
    assert len(alerts) >= 1
    a = alerts[0]
    assert a["subtype"] == "blight"
    assert a["reports_count"] == 3
    assert len(a["remedies"]) >= 2
    # Check cheapest first
    costs = [r["cost_acre"] for r in a["remedies"]]
    assert costs == sorted(costs)

def test_radar_heatmap_grid():
    reports = [{"lat": 28.615, "lon": 77.210, "weight": 1.0}]
    grid = compute_heatmap(reports, grid_size=5)
    assert len(grid) == 25
    intensities = [pt["intensity"] for pt in grid]
    assert max(intensities) > 0.5
    assert min(intensities) >= 0.0
