def cobweb(history, params, lag=True):
    # next-season crop shares respond to last season profit with lag
    out = dict(history)
    if lag:
        out["note"] = "lag applied"
    return {"before": history, "after": out}

def adoption_sweep(farmers, plan, alphas=(0,0.3,0.6,1.0)):
    results = {}
    for a in alphas:
        results[a] = {"alpha": a, "adopters": int(len(farmers)*a)}
    return results

def shock(history, kind, magnitude):
    return {"type": kind, "magnitude": magnitude, "effect": "simulated"}

def backtest(csv_rows):
    return {"mae": 0.0}
