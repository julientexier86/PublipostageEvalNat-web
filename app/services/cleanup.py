from pathlib import Path
import shutil, time

def schedule_dir_delete(base_dir: Path, ttl_minutes: int = 30):
    if not base_dir.exists():
        return
    now = int(time.time())
    for session in base_dir.iterdir():
        tok = next(session.glob("*.tok"), None)
        if not tok:
            continue
        ts = int(tok.read_text().strip())
        if now - ts > ttl_minutes * 60:
            shutil.rmtree(session, ignore_errors=True)