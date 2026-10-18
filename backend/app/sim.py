import math
from app.glut import DEFAULT_CROP_PARAMS

def simulate_cobweb(seasons: int = 6, crop: str = "potato", K: float = 0.08) -> dict:
    """
    Cobweb supply-demand oscillation simulation:
    - Without Glut Guard: naive backward-looking supply creates extreme price volatility.
    - With Glut Guard: forward coordinated planning dampens fluctuations.
    """
    cp = DEFAULT_CROP_PARAMS.get(crop, DEFAULT_CROP_PARAMS["potato"])
    p0 = cp["P0"]
    d_target = cp["demand"]
    cost = cp["cost"]
    yield_rate = cp["yield"]
    
    uncoord = []
    coord = []
    
    # Initial state
    s_uncoord = d_target * 0.7  # Initial shortage
    s_coord = d_target * 0.7
    
    for s in range(1, seasons + 1):
        # 1. Uncoordinated (Naive reaction to previous price)
        p_uncoord = max(0.3 * p0, min(1.8 * p0, p0 * (1.0 - K * ((s_uncoord / d_target) - 1.0))))
        rev_u = s_uncoord * p_uncoord
        prof_u = rev_u - (s_uncoord / yield_rate) * cost
        
        uncoord.append({
            "season": s,
            "season_name": f"सीजन {s}",
            "supply": round(s_uncoord, 1),
            "price": round(p_uncoord, 2),
            "revenue": round(rev_u, 0),
            "profit": round(prof_u, 0)
        })
        
        # Next uncoordinated supply responds aggressively to current price
        # High price -> over-production; low price -> crash
        elasticity_supply = 1.2
        price_signal = (p_uncoord / p0) - 1.0
        s_uncoord = max(0.4 * d_target, min(1.9 * d_target, d_target * (1.0 + elasticity_supply * price_signal)))
        
        # 2. Coordinated with Glut Guard (Damped, planned against demand)
        p_coord = max(0.7 * p0, min(1.3 * p0, p0 * (1.0 - (K * 0.4) * ((s_coord / d_target) - 1.0))))
        rev_c = s_coord * p_coord
        prof_c = rev_c - (s_coord / yield_rate) * cost
        
        coord.append({
            "season": s,
            "season_name": f"सीजन {s}",
            "supply": round(s_coord, 1),
            "price": round(p_coord, 2),
            "revenue": round(rev_c, 0),
            "profit": round(prof_c, 0)
        })
        
        # Glut Guard guides next season supply directly toward target demand
        damping_factor = 0.25
        s_coord = s_coord + damping_factor * (d_target - s_coord)
        
    prices_u = [x["price"] for x in uncoord]
    prices_c = [x["price"] for x in coord]
    
    mean_u = sum(prices_u) / len(prices_u)
    var_u = sum((x - mean_u)**2 for x in prices_u) / len(prices_u)
    volatility_u = round(math.sqrt(var_u), 2)
    
    mean_c = sum(prices_c) / len(prices_c)
    var_c = sum((x - mean_c)**2 for x in prices_c) / len(prices_c)
    volatility_c = round(math.sqrt(var_c), 2)

    return {
        "crop": crop,
        "crop_name_hi": cp.get("name_hi", crop),
        "seasons": list(range(1, seasons + 1)),
        "uncoordinated": uncoord,
        "coordinated": coord,
        "price_volatility_before": volatility_u,
        "price_volatility_after": volatility_c,
        "volatility_reduction_pct": round(((volatility_u - volatility_c) / max(volatility_u, 0.01)) * 100, 1),
        "note": "Sample data / सिमुलेशन - illustrative economic model"
    }

def simulate_adoption_sweep(plots_count: int = 30, total_area: float = 60.0) -> list[dict]:
    """
    Sweep adoption rate alpha in [0%, 20%, 40%, 60%, 80%, 100%].
    Computes village profit, price stability, and gluts prevented.
    """
    results = []
    base_village_profit = 850000.0
    max_gain = 320000.0
    
    alphas = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    for a in alphas:
        pct = int(round(a * 100))
        adopters = int(round(plots_count * a))
        
        # Diminishing returns curve for coordination
        effective_coordination = 1.0 - math.exp(-2.2 * a)
        village_profit = base_village_profit + max_gain * effective_coordination
        
        # Stability index (0 to 100)
        stability = round(35.0 + 65.0 * effective_coordination, 1)
        
        # Max crop share: starts at ~65% naive, drops to ~30% balanced
        max_share = round(0.65 - 0.35 * effective_coordination, 2)
        
        gluts_prevented = int(round(4 * a))
        
        results.append({
            "alpha": a,
            "alpha_percent": pct,
            "adopting_plots": adopters,
            "total_plots": plots_count,
            "village_profit": round(village_profit, 0),
            "profit_gain": round(village_profit - base_village_profit, 0),
            "price_stability_index": stability,
            "max_crop_share": max_share,
            "gluts_prevented": gluts_prevented,
            "label": f"{pct}% एडॉप्शन"
        })
    return results

def simulate_shock(shock_type: str = "disease", magnitude: float = 0.35) -> dict:
    """Simulate shock scenario impact and recovery."""
    baseline_revenue = 1200000.0
    loss_amount = baseline_revenue * magnitude
    recovery_gain = loss_amount * 0.65  # Glut Guard mitigates 65% of loss
    
    return {
        "shock_type": shock_type,
        "magnitude": magnitude,
        "baseline_revenue": baseline_revenue,
        "loss_without_guard": round(loss_amount, 0),
        "loss_with_guard": round(loss_amount - recovery_gain, 0),
        "saved_by_guard": round(recovery_gain, 0),
        "mitigation_pct": 65.0,
        "label": "सिमुलेशन / Simulation"
    }
