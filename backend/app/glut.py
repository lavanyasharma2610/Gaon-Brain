import random

def plan(plots, crop_params, K=0.05, max_iter=10):
    order = sorted(plots, key=lambda p: p["id"])
    # baseline: each plot's original choice priced under model
    baseline_profit = {}
    for p in plots:
        c = p.get("crop")
        cp = crop_params.get(c)
        w = p.get("week", 0)
        price = cp["P0"]
        baseline_profit[p["id"]] = p["area"]*(cp["yield"]*price - cp["cost"])
    assignment = {}
    for it in range(max_iter):
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
            # floor check
            if best_profit < baseline_profit[p["id"]]:
                # keep baseline
                assignment[p["id"]] = (p.get("crop"), p.get("week",0))
            else:
                assignment[p["id"]] = best
            c,w = assignment[p["id"]]
            supply[(c,w)] = supply.get((c,w),0) + p["area"]*crop_params[c]["yield"]
        # check convergence: no violations
        break
    return assignment
EOF
EOF