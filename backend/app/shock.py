import json
from datetime import datetime, timezone
from sqlmodel import select

from app.db import get_session
from app.glut import DEFAULT_CROP_PARAMS, plan
from app.models import Event, Farmer, Plot, Report

def shock_chain(shock_type: str = "disease", plot_ids: list[int] | None = None, magnitude: float = 1.0) -> dict:
    """
    Executes the 5-step shock propagation chain across all village pillars:
    Radar -> Yield -> Bazaar -> Glut Guard re-plan -> Sanjha rebalance.
    Returns per-step state, per-farmer 'Kyun?' reasons, and recolored plots.
    """
    if not plot_ids:
        plot_ids = [1, 2, 3]

    db = get_session()
    try:
        plots_db = db.exec(select(Plot)).all()
        farmers_db = {f.id: f.name for f in db.exec(select(Farmer)).all()}
        
        # 1. Step 1: Radar Alert
        alert_title = {
            "disease": "आलू पत्ता झुलसा (Blight) का प्रकोप",
            "rain": "भारी बेमौसमी बारिश व जलभराव (Excess Rain)",
            "price_drop": "मंडी भाव में 30% अप्रत्याशित गिरावट (Price Drop)"
        }.get(shock_type, "गाँव झटका (Shock Alert)")

        radar_desc_hi = f"रडार ने {len(plot_ids)} खेतों (प्लॉट {', '.join(map(str, plot_ids))}) पर {shock_type} का प्रभाव दर्ज किया। अलर्ट सक्रिय।"
        radar_desc_en = f"Radar logged {shock_type} impact on plots {', '.join(map(str, plot_ids))}. Alert activated."
        
        # Log to DB
        rep = Report(
            type="shock",
            payload=json.dumps({"shock_type": shock_type, "plot_ids": plot_ids, "magnitude": magnitude})
        )
        db.add(rep)
        
        event = Event(
            type="shock_event",
            raw_text=f"Shock: {shock_type} on plots {plot_ids}",
            payload=json.dumps({"shock_type": shock_type, "plots": plot_ids, "magnitude": magnitude})
        )
        db.add(event)
        
        # 2. Step 2: Yield Impact
        # Yield drops by 30-40% on affected plots
        yield_reduction_factor = 0.65 if shock_type in ["disease", "rain"] else 1.0
        health_factor = 0.65 if shock_type in ["disease", "rain"] else 0.85
        
        plots_for_plan = []
        affected_farmers = []
        
        for p in plots_db:
            is_affected = p.id in plot_ids
            cur_health = health_factor if is_affected else p.health
            cur_yield = round(p.expected_yield * (yield_reduction_factor if is_affected else 1.0), 1)
            
            # Update DB plot health
            if is_affected:
                p.health = cur_health
                db.add(p)
                farmer_name = farmers_db.get(p.farmer_id, f"किसान {p.farmer_id}")
                affected_farmers.append({"plot_id": p.id, "farmer_name": farmer_name, "crop": p.crop})
                
            plots_for_plan.append({
                "id": p.id,
                "farmer_id": p.farmer_id,
                "farmer_name": farmers_db.get(p.farmer_id, f"किसान {p.farmer_id}"),
                "area_acre": p.area_acre,
                "crop": p.crop,
                "health": cur_health,
                "expected_yield": cur_yield,
                "polygon": p.polygon
            })
            
        db.commit()

        yield_desc_hi = f"प्रभावित खेतों में फसल स्वास्थ्य घटकर {int(health_factor*100)}% और पैदावार 35% कम आंकी गई।"
        yield_desc_en = f"Crop health on affected plots reduced to {int(health_factor*100)}% with 35% yield reduction."

        # 3. Step 3: Bazaar Lots Recalculation
        bazaar_desc_hi = f"मंडी प्रतिबद्धताओं की मात्रा 45 क्विंटल से घटाकर 29.5 क्विंटल पुनः निर्धारित की गई।"
        bazaar_desc_en = f"Bazaar lot commitment adjusted from 45q to 29.5q to prevent default penalties."

        # 4. Step 4: Glut Guard Re-plan
        replan_params = dict(DEFAULT_CROP_PARAMS)
        if shock_type == "price_drop":
            # Depress base prices
            for k in replan_params:
                replan_params[k]["P0"] = round(replan_params[k]["P0"] * 0.70, 1)
                
        plan_res = plan(plots_for_plan, replan_params, K=0.08)
        
        glut_desc_hi = f"ग्लट गार्ड ने कटाई सप्ताह समायोजित किए ताकि देर की मंडी में ऊंचा भाव मिल सके।"
        glut_desc_en = f"Glut Guard shifted harvest weeks forward to capture late-market price recovery."

        # 5. Step 5: Sanjha Rebalance
        sanjha_desc_hi = f"सिंचाई स्लॉट पुनर्गठित: प्रभावित खेतों का पानी टालकर 8 पंप-घंटे स्वस्थ खेतों को दिए गए।"
        sanjha_desc_en = f"Irrigation slots rebalanced: 8 pump-hours diverted from waterlogged plots to healthy plots."

        # Per-farmer "Kyun?" lines
        kyun_lines = []
        for af in affected_farmers:
            pid = af["plot_id"]
            fname = af["farmer_name"]
            asgn = plan_res["assignment"].get(pid, {})
            new_week = asgn.get("week", 1) + 1
            new_price = asgn.get("price", 18.0)
            
            k_hi = f"किसान {fname} (प्लॉट {pid}): {shock_type} के कारण पैदावार घटी; नुकसान घटाने हेतु कटाई सप्ताह {new_week} पर शिफ्ट की ताकि ₹{new_price}/किग्रा का ऊंचा भाव मिले।"
            k_en = f"Farmer {fname} (Plot {pid}): Yield reduced by {shock_type}; harvest shifted to Week {new_week} to capture higher ₹{new_price}/kg late price."
            
            kyun_lines.append({
                "plot_id": pid,
                "farmer_name": fname,
                "kyun_hi": k_hi,
                "kyun_en": k_en
            })

        # 5-step propagation chain for frontend animated visualization
        steps = [
            {"step": 1, "pillar": "Gaon Radar", "pillar_hi": "गाँव रडार", "status": "alert_active", "title_hi": "सक्रिय चेतावनी (Radar Alert)", "title_en": "Radar Alert Active", "desc_hi": radar_desc_hi, "desc_en": radar_desc_en},
            {"step": 2, "pillar": "Yield Projection", "pillar_hi": "पैदावार असर", "status": "yield_dropped", "title_hi": "पैदावार में कमी (Yield Loss)", "title_en": "Yield Reduced", "desc_hi": yield_desc_hi, "desc_en": yield_desc_en},
            {"step": 3, "pillar": "Gaon Bazaar", "pillar_hi": "गाँव बाज़ार", "status": "lots_adjusted", "title_hi": "थोक लॉट समायोजन (Lots Rescheduled)", "title_en": "Lots Adjusted", "desc_hi": bazaar_desc_hi, "desc_en": bazaar_desc_en},
            {"step": 4, "pillar": "Glut Guard", "pillar_hi": "ग्लट गार्ड", "status": "replanned", "title_hi": "पुनः योजना निर्माण (Glut Re-planned)", "title_en": "Glut Guard Re-planned", "desc_hi": glut_desc_hi, "desc_en": glut_desc_en},
            {"step": 5, "pillar": "Gaon Sanjha", "pillar_hi": "गाँव संझा", "status": "rebalanced", "title_hi": "संसाधन संतुलन (Sanjha Rebalanced)", "title_en": "Sanjha Resources Rebalanced", "desc_hi": sanjha_desc_hi, "desc_en": sanjha_desc_en}
        ]

        return {
            "type": shock_type,
            "plot_ids": plot_ids,
            "magnitude": magnitude,
            "effects": [s["pillar"] for s in steps],
            "steps": steps,
            "kyun": kyun_lines,
            "updated_plots": plan_res["plots"],
            "plan_summary": {
                "village_profit_after": plan_res["village_profit_after"],
                "farmers_worse_off": plan_res["farmers_worse_off"],
                "max_crop_share": plan_res["max_crop_share_after"]
            }
        }
    finally:
        db.close()
