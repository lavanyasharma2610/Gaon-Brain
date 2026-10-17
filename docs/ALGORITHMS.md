# ALGORITHMS.md

## Glut Guard
- supply S(c,w) = sum(area x yield) of plots assigned (c,w)
- price(c,w) = clip(P0 x (1 - K x (S/D - 1)), 0.3*P0, 1.8*P0)
- profit(plot,c,w,scenario) = area x (yield x yield_mult x price x price_mult - cost)
- Greedy sequential assignment in deterministic seeded order; each plot picks feasible (crop,week) maximising profit given supply assigned.
- Baseline = each plot's own original choice priced under same model.
- Floor check: if planned profit < baseline in normal OR bad scenario, keep baseline. Iterate until no violations (cap iterations, report convergence).
- Rotation: plots moved last season moved last this season.

## Buyer trust score
- (on_time + 1) / (n + 2), on_time = paid within due date + 5 days. Hide when n < 3.

## Bijli window
- From power_logs per feeder, hourly P(on) = on_days/total_days; best contiguous 3-hour window; require min days of data.

## Sinchai Card
- Skip if forecast rain_mm_48h >= 10 and probability >= 60.
- Irrigate if days_since_last_irrigation >= crop interval (placeholder, adjusted by health); else wait.

## Alert rule
- >= N same-type reports within R km in D days (defaults 3/2km/5days).
EOF