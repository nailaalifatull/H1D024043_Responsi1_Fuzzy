from flask import Flask, render_template, request, jsonify
from fuzzy_engine import run_moodsync, OUTPUT_LABELS, RULE_BASE

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/calculate", methods=["POST"])
def calculate():
    data = request.get_json(silent=True) or {}

    try:
        sport_val = float(data.get("sport", 50))
        music_val = float(data.get("music", 50))
    except (TypeError, ValueError):
        return jsonify({"error": "Nilai harus berupa angka 0–100"}), 400

    result = run_moodsync(sport_val, music_val)

    # Susun fired rules untuk response
    fired_rules_data = [
        {
            "olahraga_cat": r.olahraga_cat,
            "musik_cat":    r.musik_cat,
            "output_cat":   r.output_cat,
            "mu_olahraga":  round(r.mu_olahraga, 4),
            "mu_musik":     round(r.mu_musik, 4),
            "alpha":        round(r.alpha, 4),
        }
        for r in result.fired_rules
    ]

    return jsonify({
        "sport_value":    result.sport_value,
        "music_value":    result.music_value,
        "mu_olahraga":    {k: round(v, 4) for k, v in result.mu_olahraga.items()},
        "mu_musik":       {k: round(v, 4) for k, v in result.mu_musik.items()},
        "aggregated":     {k: round(v, 4) for k, v in result.aggregated.items()},
        "fired_rules":    fired_rules_data,
        "crisp_score":    result.crisp_score,
        "category":       result.category,
        "label":          result.label,
        "recommendation": result.recommendation,
        "activities":     result.activities,
        "dominant_sport": result.dominant_sport,
        "dominant_music": result.dominant_music,
    })


@app.route("/api/rules", methods=["GET"])
def get_rules():
    """Kembalikan daftar rule base dalam format JSON."""
    rules = [
        {"no": i + 1, "olahraga": o, "musik": m, "output": OUTPUT_LABELS.get(p, p)}
        for i, (o, m, p) in enumerate(RULE_BASE)
    ]
    return jsonify(rules)


if __name__ == "__main__":
    print("=" * 55)
    print("  MoodSync — SPK Fuzzy Mamdani")
    print("  Buka browser: http://localhost:5000")
    print("=" * 55)
    app.run(debug=True, port=5000)