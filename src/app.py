#
from __future__ import annotations
import os
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv
from src.core.config import AppConfig
from src.ml.service import YOLOv8Classifier

def create_app() -> Flask:
    # 1. Ortam değişkenlerini yükle
    base_dir = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=base_dir / ".env")

    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
        static_url_path="/static",
    )

    # 2. Proxy ayarları
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_prefix=1)

    # 3. Temel Konfigürasyon (AppConfig)
    cfg = AppConfig(upload_dir=base_dir / "uploads")
    cfg.upload_dir.mkdir(parents=True, exist_ok=True)

    # --- EKSİK KALAN VE HATAYA SEBEP OLAN AYARLAR GERİ GELDİ ---
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "vibzy_2026_key")
    app.config["UPLOAD_DIR"] = str(cfg.upload_dir)
    # KeyError 'ALLOWED_EXT' hatasını çözen satır:
    app.config["ALLOWED_EXT"] = cfg.allowed_ext 
    app.config["MAX_CONTENT_LENGTH"] = cfg.max_content_length
    
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # 4. Model Ayarları (Senin orijinal ayarların + CPU/GPU seçeneği)
    app.config["MODEL_PATH"] = str(base_dir / "weights" / "best.pt")
    app.config["MODEL_IMGSZ"] = 160
    app.config["MODEL_DEVICE"] = os.environ.get("MODEL_DEVICE", "cpu")

    # 5. Model Servisini Başlat
    app.classifier = YOLOv8Classifier(
        weights_path=Path(app.config["MODEL_PATH"]),
        imgsz=int(app.config["MODEL_IMGSZ"]),
        device=str(app.config["MODEL_DEVICE"]),
    )

    # 6. Rotaları Kaydet
    from src.web.routes import bp as web_bp
    app.register_blueprint(web_bp)
    from src.ml.routes import bp as ml_bp
    app.register_blueprint(ml_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)