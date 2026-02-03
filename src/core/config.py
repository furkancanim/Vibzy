from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Set

@dataclass(frozen=True)
class AppConfig:
    upload_dir: Path
    allowed_ext: Set[str] = field(default_factory=lambda: {"jpg", "jpeg", "png", "webp"})
    max_content_length: int = 10 * 1024 * 1024  # 10 MB
    secret_key: str = "dev-secret-change-me"
