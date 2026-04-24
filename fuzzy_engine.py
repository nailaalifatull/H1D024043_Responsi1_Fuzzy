from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# 1. FUNGSI KEANGGOTAAN (Membership Functions)
# ---------------------------------------------------------------------------

def trapezoid_mf(x: float, a: float, b: float, c: float, d: float) -> float:
    if x <= a or x >= d:
        return 0.0
    if x < b:
        return (x - a) / (b - a)
    if x <= c:
        return 1.0
    return (d - x) / (d - c)


def triangle_mf(x: float, a: float, b: float, c: float) -> float:
    if x <= a or x >= c:
        return 0.0
    if x <= b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)


# ---------------------------------------------------------------------------
# 2. FUZZIFIKASI INPUT
# ---------------------------------------------------------------------------

def fuzzify_input(value: float) -> Dict[str, float]:
    return {
        "rendah": trapezoid_mf(value, 0.0, 0.0, 30.0, 45.0),
        "sedang": triangle_mf(value, 25.0, 50.0, 75.0),
        "tinggi": trapezoid_mf(value, 55.0, 70.0, 100.0, 100.0),
    }


def fuzzify_output(z: float) -> Dict[str, float]:
    return {
        "kurang_disarankan": trapezoid_mf(z, 0.0,  0.0,  20.0,  35.0),
        "netral":             triangle_mf(z, 25.0, 50.0,  70.0),
        "disarankan":         triangle_mf(z, 55.0, 70.0,  85.0),
        "sangat_disarankan":  trapezoid_mf(z, 75.0, 85.0, 100.0, 100.0),
    }


# ---------------------------------------------------------------------------
# 3. RULE BASE — 9 Aturan Mamdani
# ---------------------------------------------------------------------------

RULE_BASE: List[Tuple[str, str, str]] = [
    # (Olahraga, Musik, Output)
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


# ---------------------------------------------------------------------------
# 4. INFERENSI — MIN (implikasi) + MAX (agregasi)
# ---------------------------------------------------------------------------

@dataclass
class FiredRule:
    olahraga_cat: str
    musik_cat: str
    output_cat: str
    mu_olahraga: float          
    mu_musik: float             
    alpha: float                


@dataclass
class InferenceResult:
    mu_olahraga: Dict[str, float]
    mu_musik: Dict[str, float]
    fired_rules: List[FiredRule]
    aggregated: Dict[str, float]   


def infer(sport_val: float, music_val: float) -> InferenceResult:
    mu_o = fuzzify_input(sport_val)
    mu_m = fuzzify_input(music_val)

    # Inisialisasi agregasi (0 = tidak ada aturan aktif untuk kategori ini)
    aggregated: Dict[str, float] = {
        "kurang_disarankan": 0.0,
        "netral": 0.0,
        "disarankan": 0.0,
        "sangat_disarankan": 0.0,
    }

    fired_rules: List[FiredRule] = []

    for (o_cat, m_cat, out_cat) in RULE_BASE:
        # Operator MIN: kekuatan aturan = minimum derajat keanggotaan antecedent
        alpha = min(mu_o[o_cat], mu_m[m_cat])

        fired_rules.append(FiredRule(
            olahraga_cat=o_cat,
            musik_cat=m_cat,
            output_cat=out_cat,
            mu_olahraga=mu_o[o_cat],
            mu_musik=mu_m[m_cat],
            alpha=alpha,
        ))

        # Operator MAX: ambil alpha terbesar untuk tiap kategori output
        if alpha > aggregated[out_cat]:
            aggregated[out_cat] = alpha

    return InferenceResult(
        mu_olahraga=mu_o,
        mu_musik=mu_m,
        fired_rules=fired_rules,
        aggregated=aggregated,
    )


# ---------------------------------------------------------------------------
# 5. DEFUZZIFIKASI — Metode Centroid (Center of Gravity)
# ---------------------------------------------------------------------------

def defuzzify(aggregated: Dict[str, float], n_points: int = 1000) -> float:
    numerator = 0.0
    denominator = 0.0

    for i in range(n_points + 1):
        z = (i / n_points) * 100.0          # titik pada universe [0, 100]
        mf = fuzzify_output(z)

        # Clipping + agregasi MAX
        mu_agg = max(
            min(aggregated["kurang_disarankan"], mf["kurang_disarankan"]),
            min(aggregated["netral"],            mf["netral"]),
            min(aggregated["disarankan"],        mf["disarankan"]),
            min(aggregated["sangat_disarankan"], mf["sangat_disarankan"]),
        )

        numerator   += z * mu_agg
        denominator += mu_agg

    # Hindari pembagian nol (semua aturan alpha = 0)
    return round(numerator / denominator, 2) if denominator > 0 else 50.0


# ---------------------------------------------------------------------------
# 6. LABEL & REKOMENDASI TEKS
# ---------------------------------------------------------------------------

OUTPUT_LABELS = {
    "kurang_disarankan": "Kurang Disarankan",
    "netral":            "Netral",
    "disarankan":        "Disarankan",
    "sangat_disarankan": "Sangat Disarankan",
}

RECOMMENDATIONS = {
    "kurang_disarankan": (
        "Minat pada olahraga dan musik masih tergolong rendah. "
        "Tidak perlu terburu-buru — mulailah dengan hal-hal kecil yang menyenangkan, "
        "seperti jalan santai sore hari atau menikmati lagu favorit sambil bersantai di rumah."
    ),
    "netral": (
        "Profil minat Anda cukup seimbang dan fleksibel. "
        "Aktivitas seperti yoga ringan dengan musik latar, atau jalan kaki santai "
        "sambil mendengarkan podcast, bisa menjadi pilihan relaksasi yang nyaman."
    ),
    "disarankan": (
        "Anda memiliki minat yang cukup kuat, baik di olahraga maupun musik. "
        "Aktivitas seperti jogging pagi sambil mendengarkan playlist favorit, "
        "atau mengikuti kelas senam aerobik, sangat cocok dan memberi manfaat optimal."
    ),
    "sangat_disarankan": (
        "Profil minat Anda luar biasa! Kombinasi minat olahraga dan musik yang tinggi "
        "membuat aktivitas seperti dance workout, zumba, atau sesi gym dengan playlist "
        "energik menjadi pilihan relaksasi yang sempurna untuk Anda."
    ),
}

ACTIVITY_SUGGESTIONS = {
    "kurang_disarankan": ["Meditasi ringan", "Pernapasan dalam", "Istirahat tenang", "Membaca buku"],
    "netral":            ["Yoga dengan musik latar", "Jalan santai", "Podcast sambil bersantai", "Stretching ringan"],
    "disarankan":        ["Jogging sambil mendengarkan musik", "Senam aerobik", "Bersepeda santai", "Berenang"],
    "sangat_disarankan": ["Dance workout", "Zumba", "Gym dengan playlist energik", "Kelas fitness berbasis musik"],
}


def get_category(score: float) -> str:
    if score < 35:
        return "kurang_disarankan"
    if score < 58:
        return "netral"
    if score < 78:
        return "disarankan"
    return "sangat_disarankan"


def get_dominant_input_label(mu: Dict[str, float]) -> str:
    return max(mu, key=mu.get).capitalize()


# ---------------------------------------------------------------------------
# 7. FUNGSI UTAMA — Jalankan seluruh pipeline fuzzy
# ---------------------------------------------------------------------------

@dataclass
class MoodSyncResult:
    sport_value: float
    music_value: float
    mu_olahraga: Dict[str, float]
    mu_musik: Dict[str, float]
    fired_rules: List[FiredRule]
    aggregated: Dict[str, float]
    crisp_score: float
    category: str
    label: str
    recommendation: str
    activities: List[str]
    dominant_sport: str
    dominant_music: str


def run_moodsync(sport_val: float, music_val: float) -> MoodSyncResult:
    sport_val = max(0.0, min(100.0, float(sport_val)))
    music_val = max(0.0, min(100.0, float(music_val)))

    inf_result = infer(sport_val, music_val)

    crisp_score = defuzzify(inf_result.aggregated)

    category = get_category(crisp_score)

    return MoodSyncResult(
        sport_value=sport_val,
        music_value=music_val,
        mu_olahraga=inf_result.mu_olahraga,
        mu_musik=inf_result.mu_musik,
        fired_rules=inf_result.fired_rules,
        aggregated=inf_result.aggregated,
        crisp_score=crisp_score,
        category=category,
        label=OUTPUT_LABELS[category],
        recommendation=RECOMMENDATIONS[category],
        activities=ACTIVITY_SUGGESTIONS[category],
        dominant_sport=get_dominant_input_label(inf_result.mu_olahraga),
        dominant_music=get_dominant_input_label(inf_result.mu_musik),
    )
