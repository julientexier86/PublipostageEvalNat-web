from __future__ import annotations
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from pathlib import Path
from tempfile import TemporaryDirectory, SpooledTemporaryFile
import secrets, shutil, time, traceback, sys, os, logging
from typing import Optional

from app.services.pipeline import run_pipeline
from app.services.eml_build import build_eml_bundle
from app.services.cleanup import schedule_dir_delete
from app.services.ocr import has_text_layer, ocr_pdf
from app.services.csv_message import inject_message

MAX_UPLOAD_MB = 200
TMP_ROOT = Path("/tmp/publipostage_sessions")
TMP_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Publipostage ÉvalNat (web)")
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

logger = logging.getLogger(__name__)

async def _guard_size(up: UploadFile, dest_path: Path) -> None:
    total = 0
    with dest_path.open("wb") as f:
        while True:
            chunk = await up.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPLOAD_MB * 1024 * 1024:
                dest_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Fichier trop volumineux")
            f.write(chunk)

def _normalize_csv_utf8(csv_path: Path) -> None:
    raw = csv_path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1", errors="replace")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    csv_path.write_text(text, encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/health")
def health():
    return {"status": "ok"}

def _mask_token(token: Optional[str]) -> Optional[str]:
    if not token or len(token) <= 8:
        return token
    return token[:5] + "****" + token[-4:]

@app.get("/env")
def show_env():
    keys = ["OCR_REMOTE_URL", "OCR_REMOTE_TOKEN", "OCR_FORCE_REMOTE"]
    return JSONResponse({k: (_mask_token(os.environ.get(k)) if k == "OCR_REMOTE_TOKEN" else os.environ.get(k)) for k in keys})

def process_publipostage(
    in_dir: Path,
    out_dir: Path,
    src_pdf: Path,
    src_csv: Path,
    annee: str,
    classe: str,
    mode_eml: bool,
    no_split: bool,
    force_ocr: bool,
    ocr_lang: str,
    ocr_profile: str,
    message_text: Optional[str]
):
    # Copie du CSV source dans out/ pour fallback EML
    try:
        shutil.copy2(src_csv, out_dir / "parents_source.csv")
    except Exception as e:
        logger.warning(f"Impossible de copier le CSV source: {e}")
        
    ocrd_pdf = in_dir / "source_ocr.pdf"
    need_ocr = force_ocr or (not has_text_layer(src_pdf))
    pdf_to_use = src_pdf
    try:
        if need_ocr:
            try:
                ocr_pdf(src_pdf, ocrd_pdf, lang=ocr_lang, profile=ocr_profile)
                pdf_to_use = ocrd_pdf
            except Exception as _ocr_err:
                logger.warning(f"[OCR] échec OCR -> usage du PDF d'origine: {_ocr_err}")

        run_pipeline(
            pdf_path=pdf_to_use,
            csv_path=src_csv,
            annee=annee,
            classe=classe,
            out_dir=out_dir,
            no_split=no_split,
            message_text=message_text,
        )

        inject_message(out_dir=out_dir, message_text=message_text)

        if mode_eml:
            build_eml_bundle(out_dir=out_dir, classe=classe, annee=annee, message_text=message_text)

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"==== PIPELINE ERROR TRACEBACK ====\n{tb}")
        tail = "\n".join(tb.strip().splitlines()[-20:])
        raise HTTPException(
            status_code=400,
            detail=f"Erreur pipeline ({e.__class__.__name__}): {e}\n\nTraceback (tail):\n{tail}"
        )

@app.post("/process", response_class=HTMLResponse)
async def process(
    request: Request,
    background_tasks: BackgroundTasks,
    pdf: UploadFile = File(...),
    csv_eleve: UploadFile = File(...),
    annee: str = Form(...),
    classe: str = Form(...),
    mode_eml: bool = Form(True),
    no_split: bool = Form(False),
    force_ocr: bool = Form(False),
    ocr_lang: str = Form("fra"),
    ocr_profile: str = Form("balanced"),
    message_text: Optional[str] = Form(None),
):
    session_dir = Path(TemporaryDirectory(dir=TMP_ROOT).name)
    in_dir = session_dir / "in"
    out_dir = session_dir / "out"
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    src_pdf = in_dir / "source.pdf"
    src_csv = in_dir / "eleves.csv"
    await _guard_size(pdf, src_pdf)
    await _guard_size(csv_eleve, src_csv)

    _normalize_csv_utf8(src_csv)

    process_publipostage(
        in_dir=in_dir,
        out_dir=out_dir,
        src_pdf=src_pdf,
        src_csv=src_csv,
        annee=annee,
        classe=classe,
        mode_eml=mode_eml,
        no_split=no_split,
        force_ocr=force_ocr,
        ocr_lang=ocr_lang,
        ocr_profile=ocr_profile,
        message_text=message_text
    )

    zip_path = session_dir / f"Publipostage_{classe}_{annee}.zip"
    shutil.make_archive(zip_path.with_suffix(""), "zip", out_dir)

    token = secrets.token_urlsafe(24)
    (session_dir / f"{token}.tok").write_text(str(int(time.time())))
    background_tasks.add_task(schedule_dir_delete, base_dir=TMP_ROOT, ttl_minutes=30)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "download_url": request.url_for("download", token=token),
        "approx_size_mb": round(zip_path.stat().st_size / (1024*1024), 2),
        "expires": "30 minutes"
    })

@app.get("/download/{token}")
def download(token: str, background_tasks: BackgroundTasks):
    if not TMP_ROOT.exists():
        raise HTTPException(status_code=404, detail="Expiré")
    for session in TMP_ROOT.iterdir():
        if (session / f"{token}.tok").exists():
            zips = list(session.glob("*.zip"))
            if not zips:
                raise HTTPException(status_code=404, detail="Expiré")
            zip_path = zips[0]
            background_tasks.add_task(shutil.rmtree, session, ignore_errors=True)
            return FileResponse(
                path=zip_path,
                filename=zip_path.name,
                media_type="application/zip",
                headers={
                    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                    "Pragma": "no-cache"
                }
            )
    raise HTTPException(status_code=404, detail="Lien invalide ou expiré")
