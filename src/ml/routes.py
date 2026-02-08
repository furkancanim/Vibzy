from flask import Blueprint, request, jsonify, current_app, session
from pathlib import Path
from src.ml.gemini_service import GeminiMusicStyler
from src.fizy.fizy_service import FizyService # <-- Fizy servisini çağırdık

bp = Blueprint("ml", __name__, url_prefix="/ml")

# Servisleri başlat
music_styler = GeminiMusicStyler()
fizy_service = FizyService()

# Vibe Haritası (Senin belirlediğin Türkçe moodlar)
VIBE_MAP = {
    ("buildings", "sea"): "Mavi Metropol",
    ("buildings", "street"): "Şehrin Ritmi",
    ("forest", "mountain"): "Dumanlı Zirveler",
    ("sea", "street"): "Sahil Sürüşü",
    ("buildings", "forest"): "Şehirde Nefes",
    ("glacier", "mountain"): "Kristal Sessizlik",
    # Yedekler
    ("buildings",): "Beton Orman",
    ("street",): "Asfaltın Sesi",
    ("forest",): "Doğanın Kucağı",
    ("sea",): "Sonsuz Mavi",
    ("mountain",): "Yüksek Rakım",
    ("glacier",): "Buzul Çağı"
}

@bp.post("/predict")
def predict():
    # 1. İstek verilerini al
    data = request.get_json(silent=True) or {}
    threshold = float(data.get("threshold", 0.05)) 
    temp = float(data.get("temp", 4.0)) 

    # 2. Dosya kontrolü
    filename = session.get("last_uploaded")
    if not filename:
        return jsonify({"ok": False, "error": "Görsel yok"}), 400

    img_path = Path(current_app.config["UPLOAD_DIR"]) / filename
    if not img_path.exists():
        return jsonify({"ok": False, "error": "Dosya bulunamadı"}), 404

    # 3. YOLO ile Nesne Tanıma (GÖZLER)
    svc = current_app.classifier
    preds = svc.predict(img_path, topk=6, temperature=temp)

    # 4. Filtreleme ve Mood Belirleme
    active_vibes = [p for p in preds if p.conf >= threshold]
    if not active_vibes:
        # Hiçbir şey bulamazsa varsayılan
        mood_name = "Bilinmeyen Evren"
    else:
        # En baskın iki nesneyi alıp haritaya bakıyoruz
        active_classes = sorted([p.cls for p in active_vibes[:2]])
        # Tuple yaparak sözlükte arıyoruz
        mood_name = VIBE_MAP.get(tuple(active_classes), active_vibes[0].cls.capitalize())

    # Gemini için veriyi hazırla
    vibe_data = [{"class": p.cls, "conf": round(p.conf, 2)} for p in active_vibes]

    # --- BURASI ÇOK ÖNEMLİ: ZİNCİRLEME REAKSİYON ---

    # ADIM 5: Gemini'ye Sor (BEYİN)
    # Gemini bize "Sanatçı - Şarkı" formatında BİR METİN dönecek.
    # Örn: "Müslüm Gürses - Nilüfer" (Bu her seferinde değişir!)
    ai_suggestion_text = music_styler.get_recommendation(mood_name, vibe_data)
    
    # ADIM 6: O metni Fizy'de Ara (KULAKLAR)
    # Gemini'nin ürettiği dinamik metni Fizy'ye veriyoruz.
    fizy_result = fizy_service.search_song(ai_suggestion_text)

    # -----------------------------------------------

    # 7. Sonucu Paketle ve Gönder
    return jsonify({
        "ok": True,
        "mood": mood_name,
        "yolo_results": vibe_data,     # Ekranda grafik çizdirmek istersen diye
        "gemini_text": ai_suggestion_text, # "Müslüm Gürses - Nilüfer"
        "music": fizy_result           # {link: ..., image: ..., title: ...}
    })