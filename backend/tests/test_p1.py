from app.db import init_db, get_session
from app.seed import seed
from app.providers import PriceProvider

def test_seed_and_provider():
    init_db()
    seed()
    p = PriceProvider()
    assert p.modal_price("wheat") is not None
EOF