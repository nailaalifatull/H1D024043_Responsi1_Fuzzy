from dataclasses import dataclass
from typing import Dict, List, Tuple
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return {
        "message": "MoodSync Fuzzy Engine is active!",
        "usage": "Use /predict?sport=VAL&music=VAL (value 0-100)",
        "example": "/predict?sport=85&music=70"
    }

@app.route("/predict", methods=["GET"])
def predict():
    sport_raw = request.args.get("sport", "0")
    music_raw = request.args.get("music", "0")

    try:
        sport = float(sport_raw)
        music = float(music_raw)
        
        result = run_moodsync(sport, music)

        return jsonify({
            "status": "success",
            "data": {
                "score": result.crisp_score,
                "kategori": result.label,
                "rekomendasi": result.recommendation,
                "saran_aktivitas": result.activities,
                "analisis_input": {
                    "olahraga_dominan": result.dominant_sport,
                    "musik_dominan": result.dominant_music
                }
            }
        })
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Input 'sport' dan 'music' harus berupa angka (0-100)."
        }), 400

# ---------------------------------------------------------------------------
# LOGIKA FUZZY (MAMDANI)
# ---------------------------------------------------------------------------

def trapezoid_mf(x: float, a: float, b: float, c: float, d: float) -> float:
    if x <= a or x >= d: return 0.0
    if x < b: return (x - a) / (b - a)
    if x <= c: return 1.0
    return (d - x) / (d - c)

def triangle_mf(x: float, a: float, b: float, c: float) -> float:
    if x <= a or x >= c: return 0.0
    if x <= b: return (x - a) / (b - a)
    return (c - x) / (c - b)

def fuzzify_input(value: float) -> Dict[str, float]:
    return {
        "rendah": trapezoid_mf(value, 0.0, 0.0, 30.0, 45.0),
        "sedang": triangle_mf(value, 25.0, 50.0, 75.0),
        "tinggi": trapezoid_mf(value, 55.0, 70.0, 100.0, 100.0),
    }

def fuzzify_output(z: float) -> Dict[str, float]:
    return {
        "kurang_disarankan": trapezoid_mf(z, 0.0, 0.0, 20.0, 35.0),
        "netral": triangle_mf(z, 25.0, 50.0, 70.0),
        "disarankan": triangle_mf(z, 55.0, 70.0, 85.0),
        "sangat_disarankan": trapezoid_mf(z, 75.0, 85.0, 100.0, 100.0),
    }

RULE_BASE = [
    ("rendah", "rendah", "kurang_disarankan"),
    ("rendah", "sedang", "disarankan"),
    ("rendah", "tinggi", "sangat_disarankan"),
    ("sedang", "rendah", "disarankan"),
    ("sedang", "sedang", "netral"),
    ("sedang", "tinggi", "disarankan"),
    ("tinggi", "rendah", "sangat_disarankan"),
    ("tinggi", "sedang", "disarankan"),
    ("tinggi", "tinggi", "sangat_disarankan"),
]

@dataclass
class FiredRule:
    olahraga_cat: str; musik_cat: str; output_cat: str
    mu_olahraga: float; mu_music: float; alpha: float

@dataclass
class MoodSyncResult:
    crisp_score: float; label: str; recommendation: str
    activities: List[str]; dominant_sport: str; dominant_music: str

def infer(sport_val: float, music_val: float):
    mu_o = fuzzify_input(sport_val)
    mu_m = fuzzify_input(music_val)
    aggregated = {"kurang_disarankan": 0.0, "netral": 0.0, "disarankan": 0.0, "sangat_disarankan": 0.0}
    
    for (o_cat, m_cat, out_cat) in RULE_BASE:
        alpha = min(mu_o[o_cat], mu_m[m_cat])
        if alpha > aggregated[out_cat]:
            aggregated[out_cat] = alpha
    return mu_o, mu_m, aggregated

def defuzzify(aggregated: Dict[str, float], n_points: int = 100) -> float:
    numerator = 0.0
    denominator = 0.0
    for i in range(n_points + 1):
        z = (i / n_points) * 100.0
        mf = fuzzify_output(z)
        mu_agg = max(min(aggregated[k], mf[k]) for k in aggregated)
        numerator += z * mu_agg
        denominator += mu_agg
    return round(numerator / denominator, 2) if denominator > 0 else 50.0

# ---------------------------------------------------------------------------
# INTERPRETASI & MAPPING
# ---------------------------------------------------------------------------

OUTPUT_LABELS = {"kurang_disarankan": "Kurang Disarankan", "netral": "Netral", "disarankan": "Disarankan", "sangat_disarankan": "Sangat Disarankan"}

RECOMMENDATIONS = {
    "kurang_disarankan": "Minat rendah. Mulailah dengan hal kecil seperti jalan santai sore.",
    "netral": "Profil seimbang. Yoga ringan dengan musik latar sangat cocok.",
    "disarankan": "Minat kuat! Jogging pagi dengan playlist favorit sangat ideal.",
    "sangat_disarankan": "Luar biasa! Zumba atau Gym dengan musik energik adalah pilihan terbaik."
}

ACTIVITY_SUGGESTIONS = {
    "kurang_disarankan": ["Meditasi", "Membaca"],
    "netral": ["Yoga", "Jalan Santai"],
    "disarankan": ["Jogging", "Berenang"],
    "sangat_disarankan": ["Zumba", "Power Gym"]
}

def run_moodsync(sport_val: float, music_val: float) -> MoodSyncResult:
    sport_val = max(0.0, min(100.0, sport_val))
    music_val = max(0.0, min(100.0, music_val))
    
    mu_o, mu_m, agg = infer(sport_val, music_val)
    score = defuzzify(agg)
    
    if score < 35: cat = "kurang_disarankan"
    elif score < 58: cat = "netral"
    elif score < 78: cat = "disarankan"
    else: cat = "sangat_disarankan"

    return MoodSyncResult(
        crisp_score=score,
        label=OUTPUT_LABELS[cat],
        recommendation=RECOMMENDATIONS[cat],
        activities=ACTIVITY_SUGGESTIONS[cat],
        dominant_sport=max(mu_o, key=mu_o.get).capitalize(),
        dominant_music=max(mu_m, key=mu_m.get).capitalize()
    )

if __name__ == "__main__":
    app.run(debug=True)