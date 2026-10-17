from app.bazaar import buyer_trust


def test_buyer_trust():
    payments = [{"on_time": True} for _ in range(5)]
    assert buyer_trust(payments) is not None

def test_buyer_trust_hide():
    payments = [{"on_time": True} for _ in range(2)]
    assert buyer_trust(payments) is None
