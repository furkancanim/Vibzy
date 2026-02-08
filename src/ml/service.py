# yolo servisi
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
from ultralytics import YOLO


@dataclass
class ClassPred:
    cls: str
    conf: float


class YOLOv8Classifier:
    # lazy load
    def __init__(self, weights_path: Path, imgsz: int = 384, device: str = "cpu"):
        self.weights_path = weights_path
        self.imgsz = imgsz
        self.device = device
        self._model = None

    def _load(self) -> None:
        if self._model is not None:
            return
        if not self.weights_path.exists():
            raise FileNotFoundError(f"model bulunamadı: {self.weights_path}")
        self._model = YOLO(str(self.weights_path))

    @property
    def model(self):
        if self._model is None:
            self._load()
        return self._model

    
    def predict(self, image_path: Path, topk: int = 5, temperature: float = 2.0) -> List[ClassPred]:
        
        results = self.model(str(image_path), imgsz=self.imgsz, device=self.device, verbose=False)
        r0 = results[0]

        probs = getattr(r0, "probs", None)
        if probs is None:
            raise RuntimeError("classification çıktısı yok (probs)")

        # ham olasılıklarz
        vec = probs.data.detach().float().cpu().numpy()

        # temp scaling
    
        log_probs = np.log(vec + 1e-10) / temperature
        exp_probs = np.exp(log_probs)
        smoothed_vec = exp_probs / np.sum(exp_probs)

       
        idx = np.argsort(smoothed_vec)[::-1][:topk]

        names = getattr(self.model, "names", None) or getattr(r0, "names", None)
        if names is None:
            names = {i: str(i) for i in range(len(vec))}

        
        return [ClassPred(cls=str(names[int(i)]), conf=float(smoothed_vec[int(i)])) for i in idx]
