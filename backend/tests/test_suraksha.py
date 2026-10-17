from app.suraksha import kharid_check, sinchai_card


def test_sinchai_skip():
    assert "skip" in sinchai_card({}, {"rain_mm_48h":20,"prob":0.8}, 5, 1, 1.0)

def test_kharid_overcharge():
    r = kharid_check("urea", 500, 520, False, "dealer1")
    assert r["overcharge"] == 20
    assert r["missing_bill"] is True
