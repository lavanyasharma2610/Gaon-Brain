import random
from app.glut import DEFAULT_CROP_PARAMS, plan

def test_glut_property_no_farmer_worse_off():
    """
    Property test: Across 50 randomized village setups and random seeds,
    assert farmers_worse_off == 0 and every plot profit >= baseline profit.
    """
    crops = list(DEFAULT_CROP_PARAMS.keys())
    
    for seed in range(50):
        rng = random.Random(seed * 997 + 42)
        n_plots = rng.randint(10, 35)
        plots = []
        for i in range(n_plots):
            c = rng.choice(crops)
            plots.append({
                "id": i + 1,
                "area_acre": round(rng.uniform(0.5, 4.0), 2),
                "crop": c,
                "week": rng.randint(0, 1),
                "health": round(rng.uniform(0.7, 1.0), 2),
                "expected_yield": round(rng.uniform(600, 3000), 1),
                "moved_last": rng.choice([True, False])
            })
            
        k = round(rng.uniform(0.02, 0.10), 3)
        res = plan(plots, DEFAULT_CROP_PARAMS, K=k)
        
        # 1. Assert exactly zero farmers worse off
        assert res["farmers_worse_off"] == 0, f"Seed {seed} failed: farmers_worse_off={res['farmers_worse_off']}"
        
        # 2. Assert every single plot profit >= baseline profit
        for pid, asgn in res["assignment"].items():
            profit = asgn["profit"]
            base = asgn["baseline_profit"]
            assert profit >= base - 1e-4, f"Seed {seed}, Plot {pid}: profit {profit} < baseline {base}"
            
        # 3. Assert village profit is non-decreasing
        assert res["village_profit_after"] >= res["village_profit_before"] - 1e-4, (
            f"Seed {seed}: village profit after {res['village_profit_after']} < before {res['village_profit_before']}"
        )
        
        # 4. Assert all plots have valid Kyun explanations
        for pid, exp in res["explanations"].items():
            assert "hi" in exp and len(exp["hi"]) > 10
            assert "en" in exp and len(exp["en"]) > 10

def test_glut_max_crop_share_diversification():
    """When a single crop is heavily over-planted, Glut Guard must diversify and not increase max share."""
    # 20 plots all originally planting wheat
    plots = [
        {"id": i, "area_acre": 2.0, "crop": "wheat", "week": 0, "health": 1.0}
        for i in range(20)
    ]
    res = plan(plots, DEFAULT_CROP_PARAMS, K=0.08)
    assert res["farmers_worse_off"] == 0
    # Before, wheat had 100% share (1.0). Glut Guard should reduce it or not increase it.
    assert res["max_crop_share_after"] <= res["max_crop_share_before"] + 1e-4
    assert res["max_crop_share_after"] < 1.0
