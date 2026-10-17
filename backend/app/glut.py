import random

def plan(plots, crop_params, K=0.05):
    # greedy sequential assignment
    order = sorted(plots, key=lambda p: p["id"])
    assignment = {}
    supply = {}
    for p in order:
        best = None; best_profit = -1e18
        for c, cp in crop_params.items():
            for w in cp["weeks"]:
                S = supply.get((c,w),0) + p["area"]*cp["yield"]
                D = cp["demand"]
                price = cp["P0"]*(1 - K*(S/D - 1))
                price = max(0.3*cp["P0"], min(1.8*cp["P0"], price))
                profit = p["area"]*(cp["yield"]*price - cp["cost"])
                if profit > best_profit:
                    best_profit = profit; best = (c,w)
        assignment[p["id"]] = best
        c,w = best
        supply[(c,w)] = supply.get((c,w),0) + p["area"]*crop_params[c]["yield"]
    return assignment
EOF