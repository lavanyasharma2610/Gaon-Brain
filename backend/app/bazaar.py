def build_lots(plan_items):
    return []

def buyer_trust(payments):
    # (on_time+1)/(n+2)
    n = len(payments)
    on_time = sum(1 for p in payments if p.get("on_time"))
    if n < 3:
        return None
    return (on_time+1)/(n+2)
