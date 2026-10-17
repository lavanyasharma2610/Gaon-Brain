from app.shock import shock_chain
from app.sim import adoption_sweep, cobweb


def test_shock():
    r = shock_chain("disease", [1,2,3], 1)
    assert "Radar" in r["effects"]

def test_sim():
    assert cobweb({"a":1}, {}) is not None
    assert adoption_sweep([1,2,3], {}) is not None
