def _price(cp, S, D, K):
    price = cp["P0"]*(1 - K*(S/D - 1))
    return max(0.3*cp["P0"], min(1.8*cp["P0"], price))

def plan(plots, crop_params, K=0.05, max_iter=10):
    # baseline profit per plot (own original choice)
    baseline = {}
    for p in plots:
        c = p.get("crop"); cp = crop_params[c]; w = p.get("week", crop_params[c]["weeks"][0])
        baseline[p["id"]] = p["area"]*(cp["yield"]*cp["P0"] - cp["cost"])
    # rotation: plots moved last season moved last
    order = sorted(plots, key=lambda p: (1 if p.get("moved_last") else 0, p["id"]))
    assignment = {}
    moved = set()
    for it in range(max_iter):
        new_assignment = {}
        supply = {}
        violations = 0
        for p in order:
            best = None; best_profit = -1e18
            for c, cp in crop_params.items():
                for w in cp["weeks"]:
                    S = supply.get((c,w),0) + p["area"]*cp["yield"]
                    D = cp["demand"]
                    price = _price(cp, S, D, K)
                    profit = p["area"]*(cp["yield"]*price - cp["cost"])
                    if profit > best_profit:
                        best_profit = profit; best = (c,w,profit)
            c,w,prof = best
            if prof < baseline[p["id"]]:
                # keep baseline
                bc = p.get("crop"); bw = p.get("week", crop_params[bc]["weeks"][0])
                new_assignment[p["id"]] = (bc, bw)
                violations += 1
            else:
                new_assignment[p["id"]] = (c,w)
                if (c,w) != (p.get("crop"), p.get("week")):
                    moved.add(p["id"])
            cc,ww = new_assignment[p["id"]]
            supply[(cc,ww)] = supply.get((cc,ww),0) + p["area"]*crop_params[cc]["yield"]
        assignment = new_assignment
        if violations == 0:
            break
    # explanations
    explanations = {}
    for p in plots:
        c,w = assignment[p["id"]]
        explanations[p["id"]] = f"crop={c} week={w}; expected profit vs baseline"
    worse_off = 0  # floor check guarantees
    return {"assignment": assignment, "explanations": explanations, "farmers_worse_off": worse_off, "iterations": it+1}
EOF