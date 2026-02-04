#
from flask import Blueprint, request, jsonify, current_app, session
from pathlib import Path

bp = Blueprint("ml", __name__, url_prefix="/ml")

# VIBE KÜTÜPHANESİ: Sınıf ikililerini alfabetik sırayla eşler
VIBE_MAP = {
    ("buildings", "street"): "Urban_Jungle",
    ("forest", "mountain"): "Alpine_Escape",
    ("sea", "street"): "Coastal_Drive",
    ("glacier", "sea"): "Arctic_Solitude",
    ("buildings", "forest"): "City_Oasis",
    ("glacier", "mountain"): "Wilderness_Peak"
}

@bp.post("/predict")
def predict():
    data = request.get_json(silent=True) or {}
    
    # - Parametreler
    threshold = float(data.get("threshold", 0.15))
    temp = float(data.get("temp", 2.0))

    # --- KRİTİK DÜZELTME: web/routes.py'daki anahtarı kullanıyoruz ---
    filename = session.get("last_uploaded") #
    
    if not filename:
        return jsonify({
            "ok": False, 
            "error": "Oturumda dosya bulunamadı. Lütfen önce görsel yükleyin."
        }), 400

    # app.py'daki konfigürasyon anahtarı 'UPLOAD_DIR'
    upload_dir = current_app.config.get("UPLOAD_DIR")
    img_path = Path(upload_dir) / filename

    if not img_path.exists():
        return jsonify({"ok": False, "error": f"Fiziksel dosya kayıp: {filename}"}), 404

    # Tahmin işlemi
    svc = current_app.classifier
    preds = svc.predict(img_path, topk=6, temperature=temp)

    # Vibe Karışım Analizi
    active_vibes = [p for p in preds if p.conf >= threshold]
    if not active_vibes:
        active_vibes = [preds[0]]

    # İkili kombinasyonları kontrol et (alfabetik sıralama ile)
    active_classes = sorted([p.cls for p in active_vibes[:2]])
    vibe_tuple = tuple(active_classes)
    
    mood_name = VIBE_MAP.get(vibe_tuple, active_vibes[0].cls.capitalize())

    return jsonify({
        "ok": True,
        "mood": mood_name,
        "filename": filename,
        "vibe_mix": [{"class": p.cls, "conf": round(p.conf, 2)} for p in active_vibes]
    })