"""Création d'une archive de messages importable dans Zimbra."""
from __future__ import annotations

import tarfile
from pathlib import Path


def build_zimbra_bundle(out_dir: Path) -> Path | None:
    """Emballe les brouillons EML dans un TGZ pris en charge par l'import Zimbra.

    Le dossier interne isole la campagne dans la boîte Zimbra de l'utilisateur.
    Aucun identifiant Zimbra n'est demandé ou stocké par l'application.
    """
    out_dir = Path(out_dir)
    eml_files = sorted((out_dir / "eml").glob("*.eml"))
    if not eml_files:
        return None

    bundle = out_dir / "zimbra_publipostage_evalnat.tgz"
    with tarfile.open(bundle, "w:gz") as archive:
        for eml in eml_files:
            archive.add(eml, arcname=f"Publipostage_EvalNat/{eml.name}")
    return bundle
