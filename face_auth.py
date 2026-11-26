"""Verifikasi wajah lokal SecureVault menggunakan OpenCV LBPH."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np

MODEL_DIR = Path("data/face_models")
FACE_SIZE = (200, 200)
DEFAULT_THRESHOLD = 65.0


def _model_path(username: str) -> Path:
    safe_id = hashlib.sha256(username.strip().lower().encode("utf-8")).hexdigest()[:24]
    return MODEL_DIR / f"{safe_id}.yml"


def remove_face_model(username: str) -> None:
    """Hapus model wajah jika proses pembuatan akun gagal."""
    path = _model_path(username)
    if path.is_file():
        path.unlink()


def _detector():
    cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(str(cascade_path))
    if detector.empty():
        raise RuntimeError("Model deteksi wajah OpenCV tidak dapat dimuat.")
    return detector


def _extract_face(image_bytes: bytes) -> np.ndarray:
    if not image_bytes:
        raise ValueError("Foto kamera kosong.")
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Format foto tidak dapat dibaca.")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    faces = _detector().detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
    )
    if len(faces) == 0:
        raise ValueError("Wajah tidak terdeteksi. Hadapkan wajah ke kamera dan tambah pencahayaan.")
    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
    crop = gray[y:y + h, x:x + w]
    return cv2.resize(crop, FACE_SIZE, interpolation=cv2.INTER_AREA)


def enroll_face(username: str, photo_bytes: Iterable[bytes]) -> tuple[bool, str]:
    username = username.strip()
    if not username:
        return False, "Username kosong."
    photos = list(photo_bytes)
    if len(photos) < 5:
        return False, "Ambil minimal 5 foto wajah untuk pendaftaran."
    faces = []
    try:
        for index, photo in enumerate(photos, start=1):
            try:
                faces.append(_extract_face(photo))
            except ValueError as exc:
                return False, f"Foto {index}: {exc}"
        if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
            return False, "Modul OpenCV-contrib belum terpasang. Jalankan pip install opencv-contrib-python-headless."
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        labels = np.zeros(len(faces), dtype=np.int32)
        recognizer.train(faces, labels)
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        recognizer.write(str(_model_path(username)))
        return True, "Pendaftaran wajah berhasil. Model disimpan di perangkat ini."
    except Exception as exc:
        return False, f"Pendaftaran wajah gagal: {exc}"


def verify_face(username: str, photo_bytes: bytes, threshold: float = DEFAULT_THRESHOLD) -> tuple[bool, str]:
    model_path = _model_path(username)
    if not model_path.is_file():
        return False, "Data wajah belum terdaftar untuk akun ini."
    try:
        if not hasattr(cv2, "face") or not hasattr(cv2.face, "LBPHFaceRecognizer_create"):
            return False, "Modul OpenCV-contrib belum terpasang. Jalankan pip install opencv-contrib-python-headless."
        face = _extract_face(photo_bytes)
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(str(model_path))
        label, confidence = recognizer.predict(face)
        if label == 0 and confidence <= threshold:
            return True, f"Wajah cocok (skor kemiripan {confidence:.1f})."
        return False, f"Wajah tidak cocok (skor {confidence:.1f}). Coba lagi dengan pencahayaan cukup."
    except Exception as exc:
        return False, f"Verifikasi wajah gagal: {exc}"
