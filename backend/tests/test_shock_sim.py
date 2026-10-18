from app.shock import shock_chain
from app.sim import simulate_adoption_sweep, simulate_cobweb, simulate_shock

def test_shock_chain_five_steps():
    r = shock_chain("disease", [1, 2, 3], 1.0)
    assert len(r["steps"]) == 5
    pillars = [s["pillar"] for s in r["steps"]]
    assert "Gaon Radar" in pillars
    assert "Yield Projection" in pillars
    assert "Gaon Bazaar" in pillars
    assert "Glut Guard" in pillars
    assert "Gaon Sanjha" in pillars
    
    # Assert per-farmer Kyun reasons exist
    assert len(r["kyun"]) >= 1
    for k in r["kyun"]:
        assert "kyun_hi" in k and len(k["kyun_hi"]) > 10
        assert "kyun_en" in k and len(k["kyun_en"]) > 10

def test_shock_chain_rain():
    r = shock_chain("rain", [4, 5], 1.0)
    assert len(r["steps"]) == 5
    assert len(r["kyun"]) >= 1

def test_simulation_cobweb():
    r = simulate_cobweb(seasons=6, crop="potato")
    assert len(r["uncoordinated"]) == 6
    assert len(r["coordinated"]) == 6
    assert r["price_volatility_after"] <= r["price_volatility_before"]
    assert "volatility_reduction_pct" in r

def test_simulation_adoption_sweep():
    r = simulate_adoption_sweep(plots_count=30, total_area=60.0)
    assert len(r) == 6
    alphas = [x["alpha"] for x in r]
    assert 0.0 in alphas and 1.0 in alphas
    # Profit increases with adoption
    assert r[-1]["village_profit"] > r[0]["village_profit"]
    # Stability increases with adoption
    assert r[-1]["price_stability_index"] > r[0]["price_stability_index"]

def test_simulation_shock():
    r = simulate_shock(shock_type="disease", magnitude=0.35)
    assert r["saved_by_guard"] > 0
    assert r["mitigation_pct"] > 50.0
