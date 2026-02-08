from __future__ import annotations

from pathlib import Path
from flask import (
    Blueprint, current_app, render_template, request, redirect, url_for,
    flash, send_from_directory, session, abort
)

from src.core.utils import get_extension, safe_name, unique_filename

bp = Blueprint("web", __name__)


def _upload_dir() -> Path:
    return Path(current_app.config["UPLOAD_DIR"])


def _allowed(ext: str) -> bool:
    return ext in current_app.config["ALLOWED_EXT"]


@bp.get("/")
def index():

    uploaded = session.get("last_uploaded") #last uploaded
    return render_template("index.html", uploaded=uploaded)


@bp.post("/upload")
def upload():
    # not: form alanı kontrolü
    if "file" not in request.files:
        flash("dosya bulunamadı", "error")
        return redirect(url_for("web.index"))

    f = request.files["file"]
    if not f or f.filename == "":
        flash("dosya seçmelisin", "error")
        return redirect(url_for("web.index"))

    # uzantikontrolu duzeltme
    orig = safe_name(f.filename)
    ext = get_extension(orig)
    if not _allowed(ext):
        flash("bu dosya türü desteklenmiyor", "error")
        return redirect(url_for("web.index"))

    # uniquefilename
    stored = unique_filename(ext, prefix="u_")
    f.save(_upload_dir() / stored)

    # last upload session 
    session["last_uploaded"] = stored

    flash("yüklendi", "success")
    return redirect(url_for("web.index"))


@bp.get("/uploads/<path:filename>")
def uploaded_file(filename: str):
    last = session.get("last_uploaded")
    #IDOR insecure direct object reference
    if not last or filename != last: 
        abort(404)

    return send_from_directory(str(_upload_dir()), filename)
