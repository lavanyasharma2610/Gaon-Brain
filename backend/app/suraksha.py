def sinchai_card(plot, weather, crop_interval, days_since_irrigation, health):
    if weather.get("rain_mm_48h",0) >= 10 and weather.get("prob",0) >= 0.6:
        return "skip (rain expected)"
    if days_since_irrigation >= crop_interval:
        return "irrigate"
    return "wait"

def kharid_check(product, mrp, paid, bill_received, dealer):
    overcharge = paid - mrp
    flag_bill = not bill_received
    return {"overcharge": overcharge, "missing_bill": flag_bill, "dealer": dealer}

def claim_kit(farmer, policy, survey, crop, area):
    return {"farmer": farmer, "policy": policy, "survey": survey, "crop": crop, "area": area}
EOF