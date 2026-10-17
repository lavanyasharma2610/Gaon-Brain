from app.radar import haversine

def test_haversine():
    d = haversine(0,0,0,0)
    assert d == 0
EOF