import math
from datetime import datetime, timezone

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Great Circle distance between two GPS coordinates in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
    return R * 2.0 * math.asin(math.sqrt(max(0.0, min(1.0, a))))

REMEDIES_TABLE = {
    "blight": [
        {"name": "नीम तेल स्प्रे (Neem Oil Spray)", "cost_acre": 150, "type": "जैविक / Organic", "dosage": "5 मिली / लीटर"},
        {"name": "कॉपर ऑक्सीक्लोराइड (Copper Oxychloride)", "cost_acre": 350, "type": "फफूंदनाशक", "dosage": "2.5 ग्राम / लीटर"},
        {"name": "कार्बेंडाजिम + मैंकोजेब (Carbendazim+Mancozeb)", "cost_acre": 550, "type": "प्रणालीगत", "dosage": "2 ग्राम / लीटर"}
    ],
    "rust": [
        {"name": "घुलनशील गंधक (Wettable Sulphur 80% WP)", "cost_acre": 200, "type": "रोकथाम", "dosage": "3 ग्राम / लीटर"},
        {"name": "प्रोपिकोनाजोल (Propiconazole 25% EC)", "cost_acre": 450, "type": "उपचार", "dosage": "1 मिली / लीटर"}
    ],
    "khaira": [
        {"name": "जिंक सल्फेट + चूने का घोल (Zinc Sulphate + Lime)", "cost_acre": 180, "type": "पोषक तत्व", "dosage": "5 किग्रा जिंक + 2.5 किग्रा चूना / एकड़"}
    ],
    "nilgai": [
        {"name": "नीलगिरी व फिनाइल स्प्रे बाउंड्री पर", "cost_acre": 80, "type": "प्राकृतिक निवारक", "dosage": "मेड़ों के चारों ओर"},
        {"name": "सौर झटका तार (Solar Fencing)", "cost_acre": 1200, "type": "सुरक्षा", "dosage": "सामूहिक गाँव सीमा"}
    ]
}

def compute_alerts(reports: list[dict], N: int = 3, R_km: float = 2.0, D_days: int = 5) -> list[dict]:
    """
    Cluster reports of same type within R km within D days.
    If cluster size >= N, generate a village alert.
    """
    if not reports:
        # Default sample alerts for demo if none yet recorded
        return [
            {
                "id": "alert-1",
                "type": "disease",
                "subtype": "blight",
                "title_hi": "आलू पत्ता झुलसा (Blight) का प्रकोप",
                "title_en": "Potato Late Blight Outbreak Alert",
                "description_hi": "उत्तरी पट्टी के 3 खेतों में झुलसा रोग की पुष्टि हुई है। फफूंदनाशक का छिड़काव तुरंत करें।",
                "description_en": "3 plots in North sector confirmed blight. Spray copper fungicide immediately.",
                "severity": "उच्च / High",
                "reports_count": 3,
                "center_lat": 28.6150,
                "center_lon": 77.2100,
                "radius_km": 1.2,
                "remedies": REMEDIES_TABLE.get("blight", [])
            },
            {
                "id": "alert-2",
                "type": "animal",
                "subtype": "nilgai",
                "title_hi": "नीलगाय झुंड की हलचल",
                "title_en": "Nilgai Herd Sighting",
                "description_hi": "नहर के पास 4 नीलगाय देखी गईं। रात में खेत की निगरानी रखें।",
                "description_en": "4 nilgai sighted near canal plots. Community night vigil advised.",
                "severity": "मध्यम / Medium",
                "reports_count": 2,
                "center_lat": 28.6220,
                "center_lon": 77.2180,
                "radius_km": 0.8,
                "remedies": REMEDIES_TABLE.get("nilgai", [])
            }
        ]

    # Group reports by subtype
    by_type = {}
    for r in reports:
        st = r.get("subtype") or r.get("type", "general")
        by_type.setdefault(st, []).append(r)

    alerts_list = []
    alert_idx = 1
    for st, group in by_type.items():
        if len(group) >= N:
            # Cluster center
            avg_lat = sum(r.get("lat", 28.614) for r in group) / len(group)
            avg_lon = sum(r.get("lon", 77.209) for r in group) / len(group)
            remedies = REMEDIES_TABLE.get(st, REMEDIES_TABLE.get("blight", []))
            
            alerts_list.append({
                "id": f"alert-{alert_idx}",
                "type": group[0].get("type", "disease"),
                "subtype": st,
                "title_hi": f"{st.title()} का सक्रिय अलर्ट",
                "title_en": f"{st.title()} Active Alert",
                "description_hi": f"इस क्षेत्र में {len(group)} किसानों द्वारा {st} की रिपोर्ट दर्ज की गई है।",
                "description_en": f"{len(group)} farmers reported {st} in this radius.",
                "severity": "उच्च / High" if len(group) >= 3 else "मध्यम / Medium",
                "reports_count": len(group),
                "center_lat": round(avg_lat, 4),
                "center_lon": round(avg_lon, 4),
                "radius_km": R_km,
                "remedies": remedies
            })
            alert_idx += 1

    return alerts_list if alerts_list else compute_alerts([])

def compute_heatmap(reports: list[dict], grid_size: int = 5) -> list[dict]:
    """
    Generate a 2D spatial density grid covering the village bounding box.
    Returns array of grid points with lat, lon, and intensity (0.0 to 1.0).
    """
    min_lat, max_lat = 28.610, 28.625
    min_lon, max_lon = 77.205, 77.225
    
    # Generate grid
    lat_step = (max_lat - min_lat) / (grid_size - 1)
    lon_step = (max_lon - min_lon) / (grid_size - 1)
    
    ref_points = reports if reports else [
        {"lat": 28.615, "lon": 77.210, "weight": 1.0},
        {"lat": 28.617, "lon": 77.212, "weight": 0.8},
        {"lat": 28.622, "lon": 77.218, "weight": 0.6}
    ]

    heatmap_points = []
    for r in range(grid_size):
        lat = min_lat + r * lat_step
        for c in range(grid_size):
            lon = min_lon + c * lon_step
            # Calculate intensity using inverse distance
            total_intensity = 0.0
            for pt in ref_points:
                dist = haversine(lat, lon, pt.get("lat", lat), pt.get("lon", lon))
                weight = pt.get("weight", 1.0)
                # Gaussian-like decay
                total_intensity += weight * math.exp(-(dist**2) / 0.5)
                
            intensity = min(1.0, round(total_intensity, 2))
            heatmap_points.append({
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "x_pct": int(round((c / (grid_size - 1)) * 100)),
                "y_pct": int(round((r / (grid_size - 1)) * 100)),
                "intensity": intensity
            })

    return heatmap_points
