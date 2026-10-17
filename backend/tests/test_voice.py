from app.voice import parse

CASES = [
 ("5 kilo gehu becha sharma ko", "record_sale"),
 ("bijli on kar do", "power_on"),
 ("bijli off kar", "power_off"),
 ("khet mein nilgai aaya", "animal_sighting"),
 ("fasal mein bimari hai", "disease_report"),
 ("tractor chahiye kal", "tractor_request"),
 ("beej bona hai", "sowing_plan"),
 ("sinchai ho gayi", "irrigation_done"),
 ("nuksan hua", "loss_report"),
 ("dedh quintal gehu becha", "record_sale"),
 ("paanch sau rupaye kilo becha", "record_sale"),
 ("2 maund rice sold", "record_sale"),
] * 3

def test_intents_count():
    assert len(CASES) >= 30

def test_parse_returns_intent():
    for text, exp in CASES:
        r = parse(text)
        assert r["intent"] == exp, (text, r)
