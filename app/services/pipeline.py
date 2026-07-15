import re
import unicodedata
from pathlib import Path
from typing import Optional
import fitz

def _clean_text(text: str) -> str:
    """Normalise une chaîne pour la recherche Regex."""
    if not text:
        return ""
    # Enlève les accents
    nfd = unicodedata.normalize('NFD', text)
    no_acc = "".join(c for c in nfd if unicodedata.category(c) != 'Mn')
    # Remplace les retours chariots et espaces multiples par un seul espace
    return re.sub(r'\s+', ' ', no_acc).strip()

def extract_student_info(page_text: str) -> Optional[dict]:
    """
    Cherche dans le texte de la page les infos de l'élève.
    Exemple de texte attendu dans l'en-tête:
    "Nom : DUPONT Prénom : Jean Classe : 4B"
    """
    text = _clean_text(page_text)
    
    # Regex robuste non-gourmande pour attraper les noms et prénoms peu importe leurs lettres
    match = re.search(r"NOM\s*:\s*(.*?)\s*PR[EÉ]NOM\s*:\s*(.*?)\s*CLASSE\s*:\s*(\S+)", text, re.IGNORECASE)
    
    if match:
        nom = match.group(1).strip().replace(" ", "-").upper()
        prenom = match.group(2).strip().replace(" ", "-").capitalize()
        classe = match.group(3).strip().upper()
        
        # On essaie aussi d'extraire la discipline si possible (Français / Mathématiques)
        discipline = "Inconnue"
        if "FRANCAIS" in text.upper():
            discipline = "Francais"
        elif "MATHEMATIQUES" in text.upper() or "MATHS" in text.upper():
            discipline = "Mathematiques"
            
        return {
            "nom": nom,
            "prenom": prenom,
            "classe": classe,
            "discipline": discipline
        }
    return None

def run_pipeline(pdf_path: Path, csv_path: Path, annee: str, classe: str, out_dir: Path, no_split: bool = False, message_text: Optional[str] = None) -> dict[str, int]:
    """
    Découpe le PDF en fichiers individuels par élève.
    Remplace l'ancien appel lourd à legacy_pipeline.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    source = fitz.open(pdf_path)
    page_count = len(source)
    if no_split:
        destination = out_dir / f"{classe}_evaluation_nationale_{annee}.pdf"
        import shutil
        shutil.copy2(pdf_path, destination)
        source.close()
        return {"pages": page_count, "documents": 1, "unmatched": 0}

    print(f"[PIPELINE] Début découpage rapide (PyMuPDF) pour {pdf_path}")
    pages_by_document: dict[str, list[int]] = {}
    unmatched = 0
    for i, page in enumerate(source):
        text = page.get_text("text")
        info = extract_student_info(text)
        
        if info:
            # Format attendu par eml_build: CLASSE_NOM_PRENOM_DISCIPLINE_ANNEE.pdf
            # Ex: 5A_BEILLEREAU_Elie_Mathematiques_2025-2026.pdf
            filename = f"{info['classe']}_{info['nom']}_{info['prenom']}_{info['discipline']}_{annee}.pdf"
            pages_by_document.setdefault(filename, []).append(i)
        else:
            # Fallback si on ne trouve pas l'en-tête (page de garde, ou erreur OCR)
            fallback_name = f"{classe}_INCONNU_Page{i+1}_{annee}.pdf"
            output = fitz.open()
            output.insert_pdf(source, from_page=i, to_page=i)
            output.save(out_dir / fallback_name)
            output.close()
            unmatched += 1

    for filename, indexes in pages_by_document.items():
        output = fitz.open()
        for index in indexes:
            output.insert_pdf(source, from_page=index, to_page=index)
        output.save(out_dir / filename)
        output.close()

    source.close()
    print("[PIPELINE] Découpage terminé.")
    return {"pages": page_count, "documents": len(pages_by_document) + unmatched, "unmatched": unmatched}
