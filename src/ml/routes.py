


from flask import Blueprint, request, jsonify, current_app, session

from pathlib import Path
from .gemini_service import GeminiMusicStyler

bp = Blueprint("ml", __name__, url_prefix="/ml")

# geminimusic hizlansin diye onceden
music_styler = GeminiMusicStyler()

# VIBEMAP
VIBE_MAP = {
    ("buildings", "sea"): "LoFi_Chill",
    ("buildings", "street"): "HipHop",
    ("forest", "mountain"): "Huzurlu",
    ("sea", "street"): "Akustik_Chill",
    ("buildings", "forest"): "Soft",
    ("glacier", "mountain"): "Dark_Ambient"
}

@bp.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    
    
    threshold = float(data.get("threshold", 0.05)) 
    
    temp = float(data.get("temp", 4.0)) 

    filename = session.get("last_uploaded")
    if not filename:
        return jsonify({"ok": False, "error": "Görsel yok"}), 400

    img_path = Path(current_app.config["UPLOAD_DIR"]) / filename
    if not img_path.exists():
        return jsonify({"ok": False, "error": "Dosya bulunamadı"}), 404

    # YOLO
    svc = current_app.classifier
    preds = svc.predict(img_path, topk=6, temperature=temp)

    
    active_vibes = [p for p in preds if p.conf >= threshold]
    # eşik geçilmezse
    if not active_vibes: active_vibes = [preds[0]]

    # mood map filtrelemesi

    active_classes = sorted([p.cls for p in active_vibes[:2]])
    mood_name = VIBE_MAP.get(tuple(active_classes), active_vibes[0].cls.capitalize())

    # gemini verisi
    vibe_data = [{"class": p.cls, "conf": p.conf} for p in active_vibes]
    
    # muzik onerisi isteme
    ai_recommendation = music_styler.get_recommendation(mood_name, vibe_data)

    return jsonify({
        "ok": True,
        "mood": mood_name,
        "vibe_mix": [{"class": v["class"], "conf": round(v["conf"], 2)} for v in vibe_data],
        "recommendation": ai_recommendation
    })