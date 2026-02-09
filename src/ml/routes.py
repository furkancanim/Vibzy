from flask import Blueprint, request, jsonify, current_app, session
from pathlib import Path

from src.ml.gemini_service import GeminiMusicStyler

from src.ml.fizy_service import FizyService 

bp = Blueprint("ml", __name__, url_prefix="/ml")

# services
music_styler = GeminiMusicStyler()
fizy_service = FizyService()

# vibe map
VIBE_MAP = {
    ("buildings", "sea"): "Mavi Metropol",
    ("buildings", "street"): "Sokak Havası",
    ("forest", "mountain"): "Karadeniz Vibe",
    ("sea", "street"): "Sahil Yürüyüşü",
    ("buildings", "forest"): "Şehirde Ferahlık",
    ("glacier", "mountain"): "Soğuk Sessizlik",
    
    ("buildings",): "Beton Orman",
    ("street",): "Asfaltın Sesi",
    ("forest",): "Doğanın Kucağı",
    ("sea",): "Sonsuz Mavi",
    ("mountain",): "Yüksek Rakım",
    ("glacier",): "Buz Çağı"
}

@bp.post("/predict")
def predict():
    
    data = request.get_json(silent=True) or {}
    threshold = float(data.get("threshold", 0.2)) 
    temp = float(data.get("temp", 4.0)) 

    
    filename = session.get("last_uploaded")
    if not filename:
        return jsonify({"ok": False, "error": "Görsel yok"}), 400

    img_path = Path(current_app.config["UPLOAD_DIR"]) / filename
    if not img_path.exists():
        return jsonify({"ok": False, "error": "Dosya bulunamadı"}), 404

    
    svc = current_app.classifier
    preds = svc.predict(img_path, topk=6, temperature=temp)

    
    active_vibes = [p for p in preds if p.conf >= threshold]
    if not active_vibes:
        
        mood_name = "Bilinmeyen Evren"
    else:
        
        active_classes = sorted([p.cls for p in active_vibes[:2]]) 
        
        mood_name = VIBE_MAP.get(tuple(active_classes), active_vibes[0].cls.capitalize())

    
    vibe_data = [{"class": p.cls, "conf": round(p.conf, 2)} for p in active_vibes]


    ai_suggestion_text = music_styler.get_recommendation(mood_name, vibe_data)

    fizy_result = fizy_service.search_song(ai_suggestion_text)


    return jsonify({
        "ok": True,
        "mood": mood_name,
        "yolo_results": vibe_data,     
        "gemini_text": ai_suggestion_text, 
        "music": fizy_result           
    })