from __future__ import annotations

import uuid
from werkzeug.utils import secure_filename

def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()

def safe_name(filename: str) -> str:
    
    return secure_filename(filename) or "file"

def unique_filename(ext: str, prefix: str) -> str:
    ext = ext.lower().lstrip(".") or "bin"
    return f"{prefix}{uuid.uuid4().hex}.{ext}"
