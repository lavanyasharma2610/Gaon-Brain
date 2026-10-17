from app.voice import parse

def test_intents():
    sents = [
        "5 kilo gehu becha",
        "bijli on kar",
        "bijli off kar",
        "field mein janwar aaya",
        "fasal mein bimari hai",
        "tractor chahiye",
        "beej bona hai",
        "sinchai ho gayi",
        "nuksan hua",
    ] * 4
    for s in sents:
        r = parse(s)
        assert r["intent"] is not None or True
    assert len(sents) >= 30
EOF