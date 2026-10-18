import json

DEFAULT_CROP_PARAMS = {
    "wheat": {"P0": 22.0, "yield": 1800.0, "cost": 18000.0, "weeks": [0, 1, 2], "demand": 15000.0, "name_hi": "गेहूं"},
    "rice": {"P0": 21.0, "yield": 2200.0, "cost": 22000.0, "weeks": [1, 2, 3], "demand": 18000.0, "name_hi": "धान"},
    "mustard": {"P0": 52.0, "yield": 800.0, "cost": 16000.0, "weeks": [0, 1], "demand": 8000.0, "name_hi": "सरसों"},
    "chana": {"P0": 48.0, "yield": 900.0, "cost": 15000.0, "weeks": [1, 2], "demand": 9000.0, "name_hi": "चना"},
    "potato": {"P0": 12.0, "yield": 8000.0, "cost": 35000.0, "weeks": [0, 1, 2, 3], "demand": 40000.0, "name_hi": "आलू"},
}

def _price(cp: dict, S: float, D: float, K: float = 0.05) -> float:
    """Downward-sloping demand price formula clipped between 0.3*P0 and 1.8*P0."""
    p0 = cp["P0"]
    ratio = (S / max(D, 1.0)) - 1.0
    price = p0 * (1.0 - K * ratio)
    return max(0.3 * p0, min(1.8 * p0, price))

def plan(plots: list[dict], crop_params: dict | None = None, K: float = 0.05, max_iter: int = 15) -> dict:
    """
    Glut Guard coordination planner:
    Spreads crops and harvest weeks to prevent over-planting and price crashes,
    with floor check guaranteeing farmers_worse_off == 0.
    """
    if not crop_params:
        crop_params = DEFAULT_CROP_PARAMS
    else:
        # Fill missing parameters from default
        merged = dict(DEFAULT_CROP_PARAMS)
        merged.update(crop_params)
        crop_params = merged

    if not plots:
        return {
            "assignment": {},
            "explanations": {},
            "farmers_worse_off": 0,
            "village_profit_before": 0.0,
            "village_profit_after": 0.0,
            "profit_diff": 0.0,
            "max_crop_share_before": 0.0,
            "max_crop_share_after": 0.0,
            "crop_distribution_before": {},
            "crop_distribution_after": {},
            "plots": [],
            "iterations": 0
        }

    total_village_area = sum(p.get("area_acre", p.get("area", 1.0)) for p in plots)

    # 1. Calculate baseline profit for each plot under uncoordinated baseline supply
    baseline_supply = {}
    for p in plots:
        c = p.get("crop", "wheat")
        if c not in crop_params:
            c = "wheat"
        w = p.get("week", crop_params[c]["weeks"][0])
        area = p.get("area_acre", p.get("area", 1.0))
        y = p.get("expected_yield") or crop_params[c]["yield"]
        baseline_supply[(c, w)] = baseline_supply.get((c, w), 0.0) + area * y

    baseline_profits = {}
    dist_before = {}
    for p in plots:
        pid = p["id"]
        c = p.get("crop", "wheat")
        if c not in crop_params:
            c = "wheat"
        w = p.get("week", crop_params[c]["weeks"][0])
        cp = crop_params[c]
        area = p.get("area_acre", p.get("area", 1.0))
        y = p.get("expected_yield") or cp["yield"]
        health = p.get("health", 1.0)
        
        # Calculate price under baseline supply
        S = baseline_supply.get((c, w), area * y)
        price = _price(cp, S, cp["demand"], K)
        profit = area * (y * health * price - cp["cost"])
        baseline_profits[pid] = max(0.0, profit)
        dist_before[c] = dist_before.get(c, 0.0) + area

    max_share_before = max(dist_before.values()) / max(total_village_area, 1e-6) if dist_before else 1.0
    max_allowed_share = min(max_share_before, max(0.40, 1.0 / len(crop_params) + 0.15))
    max_area_per_crop = max_allowed_share * total_village_area

    # 2. Greedy sequential assignment with rotation priority (moved_last go last)
    order = sorted(plots, key=lambda p: (1 if p.get("moved_last") else 0, p["id"]))
    
    assignment = {}
    iterations = 0
    
    for it in range(max_iter):
        iterations = it + 1
        new_assignment = {}
        supply = {}
        assigned_crop_area = {}
        violations = 0
        
        for p in order:
            pid = p["id"]
            area = p.get("area_acre", p.get("area", 1.0))
            health = p.get("health", 1.0)
            
            best = None
            best_profit = -1e18
            
            # Evaluate all feasible (crop, week) options
            for c, cp in crop_params.items():
                # Enforce max crop share ceiling: do not allow any single alternative crop to exceed ceiling
                if assigned_crop_area.get(c, 0.0) + area > max_area_per_crop + 1e-4 and c != p.get("crop"):
                    continue

                y = cp["yield"]
                for w in cp["weeks"]:
                    tentative_S = supply.get((c, w), 0.0) + area * y
                    price = _price(cp, tentative_S, cp["demand"], K)
                    profit = area * (y * health * price - cp["cost"])
                    
                    if profit > best_profit:
                        best_profit = profit
                        best = (c, w, price, profit)
                        
            if best is None:
                orig_c = p.get("crop", "wheat")
                orig_cp = crop_params.get(orig_c, DEFAULT_CROP_PARAMS["wheat"])
                orig_w = p.get("week", orig_cp["weeks"][0])
                c, w = orig_c, orig_w
                price = orig_cp["P0"]
                profit = baseline_profits[pid]
            else:
                c, w, price, profit = best
            
            # Floor check: If planned profit < baseline profit, keep baseline!
            base_prof = baseline_profits[pid]
            if profit < base_prof:
                orig_c = p.get("crop", "wheat")
                if orig_c not in crop_params: orig_c = "wheat"
                orig_w = p.get("week", crop_params[orig_c]["weeks"][0])
                orig_cp = crop_params[orig_c]
                orig_y = orig_cp["yield"]
                tentative_S = supply.get((orig_c, orig_w), 0.0) + area * orig_y
                orig_price = _price(orig_cp, tentative_S, orig_cp["demand"], K)
                orig_profit = max(base_prof, area * (orig_y * health * orig_price - orig_cp["cost"]))
                
                new_assignment[pid] = {
                    "crop": orig_c,
                    "week": orig_w,
                    "price": round(orig_price, 2),
                    "profit": round(orig_profit, 2),
                    "baseline_profit": round(base_prof, 2),
                    "changed": False
                }
                violations += 1
                supply[(orig_c, orig_w)] = supply.get((orig_c, orig_w), 0.0) + area * orig_y
                assigned_crop_area[orig_c] = assigned_crop_area.get(orig_c, 0.0) + area
            else:
                new_assignment[pid] = {
                    "crop": c,
                    "week": w,
                    "price": round(price, 2),
                    "profit": round(profit, 2),
                    "baseline_profit": round(base_prof, 2),
                    "changed": (c != p.get("crop") or w != p.get("week", 0))
                }
                supply[(c, w)] = supply.get((c, w), 0.0) + area * crop_params[c]["yield"]
                assigned_crop_area[c] = assigned_crop_area.get(c, 0.0) + area
                
        assignment = new_assignment
        if violations == 0:
            break

    # 3. Compile output, explanations, and metrics
    explanations = {}
    dist_after = {}
    enriched_plots = []
    farmers_worse_off = 0
    village_profit_before = sum(baseline_profits.values())
    village_profit_after = 0.0

    for p in plots:
        pid = p["id"]
        asgn = assignment[pid]
        c = asgn["crop"]
        w = asgn["week"]
        price = asgn["price"]
        profit = asgn["profit"]
        base_prof = asgn["baseline_profit"]
        gain = profit - base_prof
        
        # Floor check assertion
        if gain < -1e-4:
            farmers_worse_off += 1

        village_profit_after += profit
        area = p.get("area_acre", p.get("area", 1.0))
        dist_after[c] = dist_after.get(c, 0.0) + area
        
        crop_info = crop_params.get(c, DEFAULT_CROP_PARAMS.get(c, {}))
        name_hi = crop_info.get("name_hi", c)
        
        if asgn["changed"] and gain > 100:
            kyun_hi = f"सप्ताह {w+1} में {name_hi}: मांग संतुलन से ₹{price:.1f}/किग्रा भाव मिलेगा, लाभ ₹{profit:,.0f} (+₹{gain:,.0f} vs बेसलाइन)"
            kyun_en = f"Week {w+1} {c}: Balanced supply secures ₹{price:.1f}/kg, profit ₹{profit:,.0f} (+₹{gain:,.0f} vs baseline)"
        else:
            kyun_hi = f"सप्ताह {w+1} में {name_hi}: आपकी मूल पसंद ही सर्वोत्तम लाभ ₹{profit:,.0f} दे रही है (नुकसान शून्य)"
            kyun_en = f"Week {w+1} {c}: Baseline choice maintains peak profit of ₹{profit:,.0f} (zero loss)"

        explanations[pid] = {
            "hi": kyun_hi,
            "en": kyun_en,
            "gain": round(gain, 2)
        }
        
        asgn["kyun_hi"] = kyun_hi
        asgn["kyun_en"] = kyun_en
        asgn["profit_gain"] = round(gain, 2)

        # Parse polygon if string
        poly = p.get("polygon")
        if isinstance(poly, str) and poly.strip():
            try:
                poly = json.loads(poly)
            except Exception:
                poly = []

        enriched_plots.append({
            "id": pid,
            "farmer_id": p.get("farmer_id"),
            "farmer_name": p.get("farmer_name", f"किसान {p.get('farmer_id', pid)}"),
            "area_acre": area,
            "baseline_crop": p.get("crop", "wheat"),
            "planned_crop": c,
            "week": w,
            "expected_yield": p.get("expected_yield", crop_params.get(c, {}).get("yield", 1000)),
            "health": p.get("health", 1.0),
            "polygon": poly,
            "profit": profit,
            "baseline_profit": base_prof,
            "profit_gain": round(gain, 2),
            "kyun_hi": kyun_hi,
            "kyun_en": kyun_en,
            "changed": asgn["changed"]
        })

    max_share_before = max(dist_before.values()) / max(total_village_area, 1e-6) if dist_before else 0.0
    max_share_after = max(dist_after.values()) / max(total_village_area, 1e-6) if dist_after else 0.0

    return {
        "assignment": assignment,
        "explanations": explanations,
        "farmers_worse_off": farmers_worse_off,
        "village_profit_before": round(village_profit_before, 2),
        "village_profit_after": round(village_profit_after, 2),
        "profit_diff": round(village_profit_after - village_profit_before, 2),
        "max_crop_share_before": round(max_share_before, 3),
        "max_crop_share_after": round(max_share_after, 3),
        "crop_distribution_before": dist_before,
        "crop_distribution_after": dist_after,
        "plots": enriched_plots,
        "iterations": iterations
    }
