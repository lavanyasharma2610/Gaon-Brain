import os
from datetime import datetime, timezone

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# Colors matching design tokens
INK = HexColor("#1E1B16")
PAPER = HexColor("#F4EFE3")
FIELD = HexColor("#3F5E3A")
TURMERIC = HexColor("#C98A12")
TERRACOTTA = HexColor("#B4492D")
INDIGO = HexColor("#2F3E6B")
RIVER = HexColor("#8A9096")

# Font setup - try to register Noto Sans Devanagari if available
FONT_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")
NOTO_REGULAR = os.path.join(FONT_DIR, "NotoSansDevanagari-Regular.ttf")
NOTO_BOLD = os.path.join(FONT_DIR, "NotoSansDevanagari-Bold.ttf")

_hindi_font_registered = False
if os.path.exists(NOTO_REGULAR):
    try:
        pdfmetrics.registerFont(TTFont("NotoDevanagari", NOTO_REGULAR))
        if os.path.exists(NOTO_BOLD):
            pdfmetrics.registerFont(TTFont("NotoDevanagari-Bold", NOTO_BOLD))
        _hindi_font_registered = True
    except Exception:
        pass

HINDI_FONT = "NotoDevanagari" if _hindi_font_registered else "Helvetica"
HINDI_FONT_BOLD = "NotoDevanagari-Bold" if _hindi_font_registered else "Helvetica-Bold"

def generate_claim_kit_pdf(data: dict, output_path: str) -> str:
    """
    Generate Claim Kit PDF dossier.
    data keys: farmer, policy_no, survey_no, crop, area, event_type, event_at,
               photos (list of dicts with sha256, lat, lon, ts, weather),
               purchases (list), sowing_record
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName=HINDI_FONT_BOLD,
        fontSize=18,
        textColor=INK,
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontName=HINDI_FONT,
        fontSize=12,
        textColor=RIVER,
        spaceAfter=12,
        alignment=TA_CENTER,
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName=HINDI_FONT_BOLD,
        fontSize=13,
        textColor=INDIGO,
        spaceBefore=14,
        spaceAfter=6,
        borderWidth=0,
        borderPadding=0,
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontName=HINDI_FONT,
        fontSize=10,
        textColor=INK,
        leading=14,
    )
    ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontName=HINDI_FONT_BOLD,
        fontSize=10,
        textColor=FIELD,
        leading=14,
    )
    ParagraphStyle(
        "ValueStyle",
        parent=styles["Normal"],
        fontName=HINDI_FONT,
        fontSize=10,
        textColor=INK,
        leading=14,
    )
    small_style = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        fontName=HINDI_FONT,
        fontSize=8,
        textColor=RIVER,
        leading=11,
    )
    disclaimer_style = ParagraphStyle(
        "DisclaimerStyle",
        parent=styles["Normal"],
        fontName=HINDI_FONT,
        fontSize=9,
        textColor=TERRACOTTA,
        leading=12,
        alignment=TA_CENTER,
        borderWidth=0.5,
        borderColor=TERRACOTTA,
        borderPadding=6,
    )

    story = []

    # Header
    story.append(Paragraph("फसल बीमा दावा डोजियर", title_style))
    story.append(Paragraph("Crop Insurance Claim Dossier", subtitle_style))
    story.append(Spacer(1, 10))

    # Disclaimer box
    story.append(Paragraph(
        "⚠ यह दस्तावेज़ केवल सहायता के लिए है। यह आधिकारिक दावा नहीं है। "
        "आधिकारिक रिपोर्टिंग: फसल बीमा ऐप या हेल्पलाइन 14447 (वर्तमान चैनल सत्यापित करें)। "
        "व्यापक उपज-हानि दावे फसल-कटाई परिणामों से तय होते हैं। SHA-256 हैश एक संकेत है, कानूनी प्रमाण नहीं।",
        disclaimer_style
    ))
    story.append(Spacer(1, 10))

    # Farmer & Policy Details
    story.append(Paragraph("किसान और नीति विवरण / Farmer & Policy Details", heading_style))
    
    farmer_data = [
        ["क्षेत्र / Field", "विवरण / Details"],
        ["किसान का नाम / Farmer Name", data.get("farmer", "-")],
        ["नीति संख्या / Policy No", data.get("policy_no", "-")],
        ["सर्वेक्षण संख्या / Survey No", data.get("survey_no", "-")],
        ["फसल / Crop", data.get("crop", "-")],
        ["बीमित क्षेत्र / Insured Area (acre)", str(data.get("area", "-"))],
        ["घटना प्रकार / Event Type", data.get("event_type", "-")],
        ["घटना दिनांक / Event Date", str(data.get("event_at", "-"))],
        ["नीति स्थिति / Policy Status", data.get("policy_status", "unknown (स्वयं-रिपोर्टेड / self-reported)")],
    ]
    
    t = Table(farmer_data, colWidths=[70*mm, 100*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), FIELD),
        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
        ("FONTNAME", (0, 0), (-1, -1), HINDI_FONT),
        ("FONTNAME", (0, 0), (-1, 0), HINDI_FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, RIVER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), PAPER]),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Sowing Record
    story.append(Paragraph("बुआई रिकॉर्ड / Sowing Record", heading_style))
    sowing = data.get("sowing_record", {})
    sowing_data = [
        ["बुआई दिनांक / Sown On", str(sowing.get("sown_on", "-"))],
        ["फसल / Crop", sowing.get("crop", "-")],
        ["क्षेत्र / Area (acre)", str(sowing.get("area_acre", "-"))],
        ["प्लॉट / Plot ID", str(sowing.get("plot_id", "-"))],
    ]
    t2 = Table(sowing_data, colWidths=[70*mm, 100*mm])
    t2.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), HINDI_FONT),
        ("FONTNAME", (0, 0), (0, -1), HINDI_FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, RIVER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [HexColor("#FFFFFF"), PAPER]),
    ]))
    story.append(t2)
    story.append(Spacer(1, 10))

    # Photos with GPS + Time + SHA-256 + Weather
    story.append(Paragraph("तस्वीरें / Photos (GPS + Time + SHA-256 + Weather)", heading_style))
    photos = data.get("photos", [])
    if photos:
        photo_data = [["#", "SHA-256", "Lat", "Lon", "Timestamp", "Weather"]]
        for i, p in enumerate(photos, 1):
            photo_data.append([
                str(i),
                p.get("sha256", "-")[:16] + "...",
                str(p.get("lat", "-")),
                str(p.get("lon", "-")),
                str(p.get("ts", "-")),
                f"Rain: {p.get('weather', {}).get('rain_mm_48h', '-')}mm, Prob: {p.get('weather', {}).get('prob', '-')}",
            ])
        t3 = Table(photo_data, colWidths=[10*mm, 35*mm, 20*mm, 20*mm, 35*mm, 50*mm])
        t3.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
            ("FONTNAME", (0, 0), (-1, -1), HINDI_FONT),
            ("FONTNAME", (0, 0), (-1, 0), HINDI_FONT_BOLD),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, RIVER),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), PAPER]),
        ]))
        story.append(t3)
    else:
        story.append(Paragraph("कोई तस्वीर नहीं / No photos uploaded", body_style))
    story.append(Spacer(1, 10))

    # Weather Snapshot
    story.append(Paragraph("मौसम स्नैपशॉट / Weather Snapshot (घटना के दिन)", heading_style))
    weather = data.get("weather_snapshot", {})
    weather_data = [
        ["पैरामीटर / Parameter", "मान / Value"],
        ["48घं बारिश / Rain 48h (mm)", str(weather.get("rain_mm_48h", "-"))],
        ["बारिश की संभावना / Rain Probability", str(weather.get("prob", "-"))],
        ["तापमान / Temp (°C)", str(weather.get("temp", "-"))],
        ["आर्द्रता / Humidity (%)", str(weather.get("humidity", "-"))],
    ]
    t4 = Table(weather_data, colWidths=[70*mm, 100*mm])
    t4.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), HINDI_FONT),
        ("FONTNAME", (0, 0), (0, -1), HINDI_FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, RIVER),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [HexColor("#FFFFFF"), PAPER]),
    ]))
    story.append(t4)
    story.append(Spacer(1, 10))

    # Related Purchases
    story.append(Paragraph("संबंधित खरीद / Related Purchases", heading_style))
    purchases = data.get("purchases", [])
    if purchases:
        pur_data = [["उत्पाद / Product", "MRP (₹)", "भुगतान / Paid (₹)", "बिल / Bill", "डीलर / Dealer"]]
        for p in purchases:
            pur_data.append([
                p.get("product", "-"),
                str(p.get("mrp", "-")),
                str(p.get("paid", "-")),
                "हाँ" if p.get("bill_received") else "नहीं",
                p.get("dealer", "-"),
            ])
        t5 = Table(pur_data, colWidths=[35*mm, 25*mm, 25*mm, 20*mm, 55*mm])
        t5.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), TERRACOTTA),
            ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#FFFFFF")),
            ("FONTNAME", (0, 0), (-1, -1), HINDI_FONT),
            ("FONTNAME", (0, 0), (-1, 0), HINDI_FONT_BOLD),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, RIVER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [HexColor("#FFFFFF"), PAPER]),
        ]))
        story.append(t5)
    else:
        story.append(Paragraph("कोई खरीद रिकॉर्ड नहीं / No purchase records", body_style))
    story.append(Spacer(1, 10))

    # Integrity Hash
    story.append(Paragraph("अखंडता हैश / Integrity Hash", heading_style))
    story.append(Paragraph(
        f"SHA-256: {data.get('dossier_hash', '-')}",
        ParagraphStyle("HashStyle", parent=body_style, fontName="Courier", fontSize=9, textColor=FIELD)
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "यह हैश दस्तावेज़ की अखंडता का संकेत है, कानूनी प्रमाण नहीं।",
        small_style
    ))
    story.append(Spacer(1, 20))

    # Official Reporting
    story.append(Paragraph("आधिकारिक रिपोर्टिंग / Official Reporting", heading_style))
    story.append(Paragraph(
        "फसल बीमा ऐप या हेल्पलाइन 14447 के माध्यम से आधिकारिक दावा दर्ज करें। "
        "वर्तमान चैनल सत्यापित करें। यह PDF केवल सहायक दस्तावेज़ है।",
        disclaimer_style
    ))
    story.append(Spacer(1, 10))

    # Generation timestamp
    story.append(Paragraph(
        f"निर्मित: {datetime.now(timezone.utc).isoformat()} UTC",
        small_style
    ))

    doc.build(story)
    return output_path


def test_claim_pdf():
    """Generate a test PDF to verify Hindi rendering."""
    import tempfile
    test_data = {
        "farmer": "राम कुमार",
        "policy_no": "PMFBY-2026-001234",
        "survey_no": "SRV-5678",
        "crop": "गेहूं / Wheat",
        "area": 2.5,
        "event_type": "अतिवृष्टि / Excess Rainfall",
        "event_at": "2026-09-15",
        "policy_status": "active (स्वयं-रिपोर्टेड)",
        "sowing_record": {"sown_on": "2026-06-20", "crop": "Wheat", "area_acre": 2.5, "plot_id": 12},
        "photos": [
            {"sha256": "a1b2c3d4e5f6..."*4, "lat": 28.6139, "lon": 77.2090, "ts": "2026-09-15T10:30:00Z", "weather": {"rain_mm_48h": 45, "prob": 0.85}},
        ],
        "weather_snapshot": {"rain_mm_48h": 45, "prob": 0.85, "temp": 28, "humidity": 78},
        "purchases": [
            {"product": "यूरिया / Urea", "mrp": 500, "paid": 520, "bill_received": False, "dealer": "Sharma Agro"},
        ],
        "dossier_hash": "deadbeef..."*8,
    }
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    generate_claim_kit_pdf(test_data, path)
    return path


if __name__ == "__main__":
    p = test_claim_pdf()
    print(f"Test PDF generated: {p}")
