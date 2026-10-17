from app.db import init_db
from app.providers import PriceProvider
from app.seed import seed


def test_seed_and_provider():
    init_db()
    seed()
    p = PriceProvider()
    assert p.modal_price("wheat") is not None
