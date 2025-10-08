from __future__ import annotations
from pathlib import Path
from typing import Optional, List
import csv

def _normalize_text(s: str) -> str:
    # Normalise les retours à \n et garantit une fin de ligne
    return (s or "").replace("\r\n", "\n").replace("\r", "\n").strip("\n") + "\n"

def inject_message(out_dir: Path, message_text: Optional[str]) -> List[Path]:
    """
    Ajoute/écrase la colonne 'Message' dans tous les CSV de out_dir
    avec le texte fourni. Renvoie la liste des CSV modifiés.
    """
    touched: List[Path] = []
    if not message_text:
        return touched

    norm = _normalize_text(message_text)

    for csv_path in out_dir.glob("*.csv"):
        try:
            with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = list(reader.fieldnames or [])
        except Exception:
            # CSV illisible → on ignore
            continue

        if not rows and not fieldnames:
            continue

        if "Message" not in fieldnames:
            fieldnames.append("Message")

        for r in rows:
            r["Message"] = norm

        tmp_path = csv_path.with_suffix(".tmp.csv")
        with open(tmp_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        tmp_path.replace(csv_path)
        touched.append(csv_path)

    return touched