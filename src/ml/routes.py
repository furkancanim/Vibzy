# not: sadece session'daki son dosya için predict
from __future__ import annotations

from pathlib import Path
from flask import Blueprint, current_app, request, jsonify, session

bp = Blueprint("ml", __name__)


def _img_path() -> Path | None:
    # not: session'da dosya yoksa predict yok
    last = session.get("last_uploaded")
    if not last:
        return None
    upload_dir = Path(current_app.config["UPLOAD_DIR"])
    p = upload_dir / last
    return p if p.exists() else None


@bp.post("/predict")
def predict():
    # not: topk opsiyonel (default 5)
    data = request.get_json(silent=True) or {}
    topk = int(data.get("topk", 5))

    img_path = _img_path()
    if img_path is None:
        return jsonify({"ok": False, "error": "önce görsel yükle"}), 400

    # not: app'e bağlanan model servisini kullan
    svc = current_app.classifier
    preds = svc.predict(img_path, topk=topk)

    return jsonify({
        "ok": True,
        "topk": [{"class": p.cls, "conf": p.conf} for p in preds],
    })
