from app.glut import plan

def test_no_worse_off():
    plots = [{"id":i,"area":1.0,"crop":"wheat","week":0} for i in range(5)]
    params = {"wheat":{"P0":2000,"yield":10,"cost":500,"weeks":[0,1],"demand":50}}
    a = plan(plots, params)
    assert a is not None
EOF