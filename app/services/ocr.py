"""OCR avec moteur local prioritaire et secours externe configurable."""
import os
import subprocess
from pathlib import Path

import requests

REMOTE_URL = os.getenv("OCR_REMOTE_URL")
REMOTE_TOKEN = os.getenv("OCR_REMOTE_TOKEN")
FORCE_REMOTE = os.getenv("OCR_FORCE_REMOTE", "0").lower() in {"1", "true", "yes"}
REMOTE_TIMEOUT = int(os.getenv("OCR_REMOTE_TIMEOUT_S", "1200"))

def has_text_layer(pdf_path: Path) -> bool:
    try:
        import fitz
        document = fitz.open(pdf_path)
        for page in document[:5]:
            if page.get_text("text").strip():
                document.close()
                return True
        document.close()
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
    """Contacte uniquement le service OCR explicitement renseigné par l'établissement."""
    if not REMOTE_URL:
        raise RuntimeError("OCR local indisponible et aucun service OCR de secours n'est configuré.")
    headers = {"Authorization": f"Bearer {REMOTE_TOKEN}"} if REMOTE_TOKEN else {}
    with input_pdf.open("rb") as source:
        response = requests.post(
            REMOTE_URL,
            headers=headers,
            files={"pdf": (input_pdf.name, source, "application/pdf")},
            data={"lang": lang, "profile": profile},
            timeout=timeout_s,
        )
    if response.status_code != 200:
        raise RuntimeError(f"Le service OCR a répondu {response.status_code}: {response.text[:200]}")
    if not response.content.startswith(b"%PDF-"):
        raise RuntimeError("Le service OCR n'a pas renvoyé un PDF valide.")
    output_pdf.write_bytes(response.content)

def ocr_pdf(input_pdf: Path, output_pdf: Path, lang: str = "fra", profile: str = "balanced", timeout_s: int = 1800):
    """Utilise le local puis un secours externe si celui-ci est explicitement configuré."""
    if FORCE_REMOTE:
        _ocr_remote(input_pdf, output_pdf, lang, profile, min(timeout_s, REMOTE_TIMEOUT))
        return
    try:
        _ocr_local(input_pdf, output_pdf, lang, profile, timeout_s)
    except (FileNotFoundError, RuntimeError) as local_error:
        if not REMOTE_URL:
            raise RuntimeError(f"OCR local indisponible : {local_error}") from local_error
        _ocr_remote(input_pdf, output_pdf, lang, profile, min(timeout_s, REMOTE_TIMEOUT))
