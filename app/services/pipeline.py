import re
import unicodedata
from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader, PdfWriter

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

def run_pipeline(pdf_path: Path, csv_path: Path, annee: str, classe: str, out_dir: Path, no_split: bool = False, message_text: Optional[str] = None):
    """
    Découpe le PDF en fichiers individuels par élève.
    Remplace l'ancien appel lourd à legacy_pipeline.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if no_split:
        print("[PIPELINE] no_split=True, on ignore la découpe.")
        return

    print(f"[PIPELINE] Début découpage natif (PyPDF2) pour {pdf_path}")
    reader = PdfReader(pdf_path)
    
    # Algorithme simple: chaque page ou groupe de pages appartient à un élève
    # Pour ÉvalNat, c'est généralement 1 page de restitution par élève par matière.
    # On itère donc page par page.
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        info = extract_student_info(text)
        
        if info:
            # Format attendu par eml_build: CLASSE_NOM_PRENOM_DISCIPLINE_ANNEE.pdf
            # Ex: 5A_BEILLEREAU_Elie_Mathematiques_2025-2026.pdf
            filename = f"{info['classe']}_{info['nom']}_{info['prenom']}_{info['discipline']}_{annee}.pdf"
            out_file = out_dir / filename
            
            writer = PdfWriter()
            writer.add_page(page)
            with out_file.open("wb") as fOut:
                writer.write(fOut)
            print(f"  -> Extrait: {filename}")
        else:
            # Fallback si on ne trouve pas l'en-tête (page de garde, ou erreur OCR)
            fallback_name = f"{classe}_INCONNU_Page{i+1}_{annee}.pdf"
            fallback_file = out_dir / fallback_name
            writer = PdfWriter()
            writer.add_page(page)
            with fallback_file.open("wb") as fOut:
                writer.write(fOut)
            print(f"  [!] En-tête non trouvé (Page {i+1}) -> {fallback_name}")

    print("[PIPELINE] Découpage terminé.")
