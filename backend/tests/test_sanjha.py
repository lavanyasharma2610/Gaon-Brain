from app.sanjha import tractor_schedule

def test_tractor_fair():
    reqs = [{"prev_served_count":2,"want_date":"2026-10-20"},{"prev_served_count":0,"want_date":"2026-10-19"}]
    ordered = tractor_schedule(reqs)
    assert ordered[0]["prev_served_count"] == 0
EOF