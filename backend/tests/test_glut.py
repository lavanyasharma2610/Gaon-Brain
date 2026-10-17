from app.glut import plan


def test_no_worse_off():
    plots = [{"id":i,"area":1.0,"crop":"wheat","week":0,"moved_last":False} for i in range(5)]
    params = {"wheat":{"P0":2000,"yield":10,"cost":500,"weeks":[0,1],"demand":50}}
    r = plan(plots, params)
    assert r["farmers_worse_off"] == 0

def test_max_share_not_increase():
    plots = [{"id":i,"area":1.0,"crop":"wheat","week":0,"moved_last":False} for i in range(5)]
    params = {"wheat":{"P0":2000,"yield":10,"cost":500,"weeks":[0,1],"demand":50},"rice":{"P0":1800,"yield":12,"cost":400,"weeks":[0,1],"demand":40}}
    r = plan(plots, params)
    assert r is not None
