# app/services/ocr.py
import os
import subprocess
from pathlib import Path
from typing import Optional

import requests

REMOTE_URL = os.getenv("OCR_REMOTE_URL")  # e.g. https://ocr.example.com/ocr
REMOTE_TOKEN = os.getenv("OCR_REMOTE_TOKEN")
FORCE_REMOTE = os.getenv("OCR_FORCE_REMOTE", "0") in {"1", "true", "True", "yes"}
REMOTE_TIMEOUT = int(os.getenv("OCR_REMOTE_TIMEOUT_S", "1200"))  # 20 minutes

def has_text_layer(pdf_path: Path) -> bool:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        for page in reader.pages[:5]:
            if (page.extract_text() or "").strip():
                return True
        return False
    except Exception:
        return False

def _ocr_local(input_pdf: Path, output_pdf: Path, lang: str, profile: str, timeout_s: int) -> None:
    args = [
        "ocrmypdf", "--skip-text", "--rotate-pages", "--deskew",
        "--language", lang, "--output-type", "pdfa",
        "--tesseract-timeout", "120", "--jobs", "2",
        "--optimize", "1",
        str(input_pdf), str(output_pdf)
    ]
    if profile == "fast":
        args = [
            "ocrmypdf", "--skip-text", "--rotate-pages", "--deskew",
            "--language", lang, "--output-type", "pdfa",
            "--tesseract-timeout", "120", "--jobs", "2",
            "--optimize", "0", "--jpeg-quality", "50", "--png-quality", "50",
            str(input_pdf), str(output_pdf)
        ]
    elif profile == "max":
        args = [
            "ocrmypdf", "--skip-text", "--rotate-pages", "--deskew",
            "--language", lang, "--output-type", "pdfa",
            "--tesseract-timeout", "120", "--jobs", "2",
            "--optimize", "3", "--jpeg-quality", "90", "--png-quality", "90",
            str(input_pdf), str(output_pdf)
        ]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout_s)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:500])

def _ocr_remote(input_pdf: Path, output_pdf: Path, lang: str, profile: str, timeout_s: int) -> None:
    if not REMOTE_URL:
        raise RuntimeError("OCR distant non configuré (OCR_REMOTE_URL manquant).")
    headers = {"Authorization": f"Bearer {REMOTE_TOKEN}"} if REMOTE_TOKEN else {}
    with open(input_pdf, "rb") as f:
        files = {"pdf": (input_pdf.name, f, "application/pdf")}
        data = {"lang": lang, "profile": profile}
        r = requests.post(REMOTE_URL, headers=headers, files=files, data=data, timeout=timeout_s)
        if r.status_code != 200:
            raise RuntimeError(f"OCR distant échec: {r.status_code} {r.text[:200]}")
        output_pdf.write_bytes(r.content)

def ocr_pdf(input_pdf: Path, output_pdf: Path, lang: str = "fra", profile: str = "balanced", timeout_s: int = 1800):
    """Effectue l'OCR en local si possible, sinon bascule sur le service distant.
    Le basculement peut être forcé avec OCR_FORCE_REMOTE=1.
    """
    if FORCE_REMOTE:
        _ocr_remote(input_pdf, output_pdf, lang, profile, min(timeout_s, REMOTE_TIMEOUT))
        return
    try:
        _ocr_local(input_pdf, output_pdf, lang, profile, timeout_s)
    except FileNotFoundError:
        # ocrmypdf/tesseract absents: on tente le distant
        _ocr_remote(input_pdf, output_pdf, lang, profile, min(timeout_s, REMOTE_TIMEOUT))