# app: flask factory + config + blueprint kaydı + model servisi
from __future__ import annotations

import os
from pathlib import Path
from flask import Flask

from src.core.config import AppConfig
from src.ml.service import YOLOv8Classifier


def create_app() -> Flask:
    # proje kökü
    base_dir = Path(__file__).resolve().parents[1]

    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
        static_url_path="/static",
    )

    # not: nginx reverse proxy headerlarını doğru yorumla (prefix dahil)
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1, x_prefix=1)

    # not: config
    cfg = AppConfig(upload_dir=base_dir / "uploads")
    cfg.upload_dir.mkdir(parents=True, exist_ok=True)

    # session için secret key
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", cfg.secret_key)

    # upload ayarları
    app.config["UPLOAD_DIR"] = str(cfg.upload_dir)
    app.config["ALLOWED_EXT"] = cfg.allowed_ext
    app.config["MAX_CONTENT_LENGTH"] = cfg.max_content_length

    # cookie güvenliği
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # not: model servisi lazy-load
    app.config["MODEL_PATH"] = str(base_dir / "weights" / "best.pt")
    app.config["MODEL_IMGSZ"] = 384
    app.config["MODEL_DEVICE"] = os.environ.get("MODEL_DEVICE", "cpu")

    app.classifier = YOLOv8Classifier(  # type: ignore[attr-defined]
        weights_path=Path(app.config["MODEL_PATH"]),
        imgsz=int(app.config["MODEL_IMGSZ"]),
        device=str(app.config["MODEL_DEVICE"]),
    )

    # not: web route'lar
    from src.web.routes import bp as web_bp
    app.register_blueprint(web_bp)

    # not: ml route'lar
    from src.ml.routes import bp as ml_bp
    app.register_blueprint(ml_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
