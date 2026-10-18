from app.voice import parse

DISTINCT_CASES = [
    # 1. Exact prompt test
    ("500 kilo aalu, 10 rupay kilo, Sharma ji ko", "record_sale", "potato", 500.0, 10.0, 5000.0),
    # 2. Hindi Devanagari digits and crop
    ("५०० किलो आलू १० रुपये किलो शर्मा जी को", "record_sale", "potato", 500.0, 10.0, 5000.0),
    # 3. Wheat sale with quintal
    ("2 quintal gehu becha 2200 rupaye quintal", "record_sale", "wheat", 200.0, 22.0, 4400.0),
    # 4. Devanagari wheat sale
    ("दो क्विंटल गेहूं बेचा बीस रुपये किलो", "record_sale", "wheat", 200.0, 20.0, 4000.0),
    # 5. Maund unit
    ("2 maund rice sold at 25 per kg to Verma", "record_sale", "rice", 80.0, 25.0, 2000.0),
    # 6. Mustard sale
    ("50 kilo sarson becha 55 rupay kilo Patel ko", "record_sale", "mustard", 50.0, 55.0, 2750.0),
    # 7. Chana sale
    ("100 kilo chana becha 48 rupaye kilo", "record_sale", "chana", 100.0, 48.0, 4800.0),
    # 8. Tomato sale
    ("30 kilo tamatar 15 rupay kilo", "record_sale", "tomato", 30.0, 15.0, 450.0),
    # 9. Onion sale
    ("80 kilo pyaz 20 rupay kilo Sharma ji", "record_sale", "onion", 80.0, 20.0, 1600.0),
    # 10. Word numbers
    ("paanch sau kilo aalu becha das rupay kilo", "record_sale", "potato", 500.0, 10.0, 5000.0),
    # 11. Dedh quintal
    ("dedh quintal dhan becha", "record_sale", "rice", 150.0, None, None),
    # 12. Power on Hinglish
    ("bijli on kar do", "power_on", None, None, None, None),
    # 13. Power on Devanagari
    ("बिजली आई चालू करो", "power_on", None, None, None, None),
    # 14. Power on variant
    ("feeder 1 power on chalu", "power_on", None, None, None, None),
    # 15. Power off Hinglish
    ("bijli off ho gayi", "power_off", None, None, None, None),
    # 16. Power off Devanagari
    ("बिजली बंद हो गई लाइट गई", "power_off", None, None, None, None),
    # 17. Power off variant
    ("motor band karo bijli gayi", "power_off", None, None, None, None),
    # 18. Animal sighting nilgai
    ("khet mein nilgai aaya hai", "animal_sighting", None, None, None, None),
    # 19. Animal sighting suvar
    ("plot 4 mein suvar ghus gaya", "animal_sighting", None, None, None, None),
    # 20. Animal sighting Devanagari
    ("खेत में जंगली जानवर और नीलगाय दिखे", "animal_sighting", None, None, None, None),
    # 21. Disease report blight
    ("aalu ki fasal mein blight bimari lag gayi", "disease_report", "potato", None, None, None),
    # 22. Disease report khaira
    ("dhan mein khaira rog dikh raha hai", "disease_report", "rice", None, None, None),
    # 23. Disease report Devanagari
    ("फसल में पत्ता झुलसा बीमारी और कीड़ा लगा है", "disease_report", None, None, None, None),
    # 24. Tractor request
    ("tractor chahiye kal jutai ke liye", "tractor_request", None, None, None, None),
    # 25. Tractor request Devanagari
    ("खेत जोतने के लिए ट्रैक्टर चाहिए", "tractor_request", None, None, None, None),
    # 26. Tractor request with date
    ("tractor service needed on 22nd", "tractor_request", None, None, None, None),
    # 27. Sowing plan
    ("agale hafte sarson ka beej bona hai", "sowing_plan", "mustard", None, None, None),
    # 28. Sowing plan Devanagari
    ("गेहूं की बुवाई की योजना बनानी है", "sowing_plan", "wheat", None, None, None),
    # 29. Irrigation done
    ("plot 12 mein sinchai ho gayi", "irrigation_done", None, None, None, None),
    # 30. Irrigation done Devanagari
    ("आज सुबह खेत में पानी दिया सिंचाई पूरी", "irrigation_done", None, None, None, None),
    # 31. Loss report
    ("barish se fasal ka bhari nuksan hua", "loss_report", None, None, None, None),
    # 32. Loss report Devanagari
    ("ओलावृष्टि से गेहूं की फसल बर्बाद हो गई", "loss_report", "wheat", None, None, None),
    # 33. Sale with bag unit (bori = 50kg)
    ("4 bori chawal becha 1200 rupaye bori Gupta ko", "record_sale", "rice", 200.0, None, None),
    # 34. Hindi script sale with full details
    ("सौ किलो चना बेचा पचास रुपये किलो शर्मा को", "record_sale", "chana", 100.0, 50.0, 5000.0),
    # 35. Pure English sale sentence
    ("Sold 500 kg potato at 12 rupees per kg to Sharma", "record_sale", "potato", 500.0, 12.0, 6000.0),
]

def test_at_least_30_distinct_sentences():
    assert len(DISTINCT_CASES) >= 30
    # Assert every sentence string is unique
    raw_sentences = [case[0] for case in DISTINCT_CASES]
    assert len(set(raw_sentences)) == len(DISTINCT_CASES)

def test_voice_prompt_hero_sentence():
    # Prompt: A farmer speaks ("500 kilo aalu, 10 rupay kilo, Sharma ji ko")
    res = parse("500 kilo aalu, 10 rupay kilo, Sharma ji ko")
    assert res["intent"] == "record_sale"
    assert res["crop"] == "potato"
    assert res["qty_kg"] == 500.0
    assert res["rate"] == 10.0
    assert res["total"] == 5000.0
    assert res["buyer"] == "sharma"
    assert res["missing"] == []

def test_deva_digits_prompt_sentence():
    res = parse("५०० किलो आलू १० रुपये किलो शर्मा जी को")
    assert res["intent"] == "record_sale"
    assert res["crop"] == "potato"
    assert res["qty_kg"] == 500.0
    assert res["rate"] == 10.0
    assert res["total"] == 5000.0

def test_all_distinct_cases():
    for text, exp_intent, exp_crop, exp_qty, exp_rate, exp_total in DISTINCT_CASES:
        res = parse(text)
        assert res["intent"] == exp_intent, f"Failed intent for: {text} -> got {res['intent']}, expected {exp_intent}"
        if exp_crop:
            assert res["crop"] == exp_crop, f"Failed crop for: {text} -> got {res['crop']}, expected {exp_crop}"
        if exp_qty is not None:
            assert res["qty_kg"] == exp_qty, f"Failed qty for: {text} -> got {res['qty_kg']}, expected {exp_qty}"
        if exp_rate is not None:
            assert res["rate"] == exp_rate, f"Failed rate for: {text} -> got {res['rate']}, expected {exp_rate}"
        if exp_total is not None:
            assert res["total"] == exp_total, f"Failed total for: {text} -> got {res['total']}, expected {exp_total}"
