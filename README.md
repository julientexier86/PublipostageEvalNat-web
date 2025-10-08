# 📨 Publipostage Évaluations Nationales Web

![Python](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Status](https://img.shields.io/badge/Status-Stable-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**Publipostage Évaluations Nationales Web** est une application web de génération automatique de fichiers PDF et d’e-mails (.eml) à partir des résultats des évaluations nationales (6e, 5e, 4e).  
Développée initialement pour un usage pédagogique et administratif, elle permet de gagner un temps considérable dans la préparation et l’envoi des documents aux familles.

---

## 🚀 Fonctionnalités principales

- **Découpe automatique** des PDF d’évaluations nationales par élève et par discipline.  
- **Fusion intelligente** avec les exports SIECLE (`CSV`) pour récupérer les coordonnées des responsables légaux.  
- **Génération automatique** des brouillons d’e-mails (`.eml`) pour chaque famille, avec pièce jointe PDF.  
- **Interface web moderne** (FastAPI + Jinja2) hébergeable sur O2switch via Passenger.  
- **Compatibilité multi-plateforme** : Windows, macOS, Linux.  
- **Option OCR** pour les PDF scannés (via `tesseract`, si disponible).  

---

## 🧭 Guide d’utilisation

### 1. Déposer les fichiers

- **PDF source** : export d’évaluations nationales (OCR possible).  
- **CSV élèves** : export SIECLE contenant les noms, prénoms et adresses mail des parents.  

### 2. Choisir les paramètres

- **Année / Classe**  
- **Mode EML** (active la génération des fichiers `.eml`)  
- **OCR automatique** (si les PDF sont scannés sans calque texte)

### 3. Télécharger le résultat

L’application produit :
- Un dossier compressé `.zip` contenant les fichiers `.eml`  
- Un fichier `parents_source.csv` pour vérification des correspondances

---

## 💡 Astuce : importer les `.eml`

1. **Windows / Thunderbird / Outlook**  
   - Glissez les `.eml` dans votre dossier “Brouillons” ou “Éléments envoyés”.  
   - Personnalisez le texte avant envoi si nécessaire.

2. **macOS / Apple Mail**  
   - Glissez les `.eml` dans Mail : ils apparaîtront comme brouillons prêts à envoyer.

3. **Webmail (Gmail, O2switch, etc.)**  
   - Non compatible avec `.eml` : ouvrez localement avec Thunderbird puis envoyez.

---

## ⚙️ Installation locale (développement)

### Prérequis

- Python ≥ 3.11  
- pip + virtualenv  
- (Optionnel... mais indispensable) Tesseract pour l’OCR (`sudo apt install tesseract-ocr` ou `brew install tesseract`)

### Installation

```bash
git clone https://github.com/julientexier86/PublipostageEvalNat-web.git
cd PublipostageEvalNat-web

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload
```

L’application sera disponible sur [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## ☁️ Déploiement sur O2switch

### Arborescence typique

```
PublipostageEvalNat-web/
├── app/
│   ├── main.py
│   ├── services/
│   └── templates/
├── legacy_cli/
│   ├── pipeline_evalnat.py
│   └── merge_parents_4e.py
├── tmp/
├── requirements.txt
├── passenger_wsgi.py
└── README.md
```

### Configuration Passenger

Dans le dossier racine :

```bash
python3 -m venv ~/virtualenv/PublipostageEvalNat-web/3.11
source ~/virtualenv/PublipostageEvalNat-web/3.11/bin/activate
pip install -r requirements.txt

touch tmp/restart.txt
```

Accès web :  
👉 [https://iyou8383.odns.fr/Publipostage](https://iyou8383.odns.fr/Publipostage)

---

## 🧩 Structure du code

| Dossier | Description |
|----------|--------------|
| `app/` | Application web FastAPI |
| `app/services/` | Modules de traitement (`pipeline`, `eml_build`, `ocr`, etc.) |
| `app/templates/` | Templates HTML Jinja2 |
| `legacy_cli/` | Code historique du pipeline local (version CLI) |
| `tmp/` | Logs & fichiers temporaires |
| `publipostage_sessions/` | Dossiers de sessions utilisateurs (créés dynamiquement) |

---

## 🧠 À propos

**Auteur :** [Julien Texier](https://github.com/julientexier86)  
**Année :** 2025  
**Objectif :** faciliter la gestion automatisée des évaluations nationales en établissement.  

> “Automatiser pour redonner du temps au sens pédagogique.”

---

## 📜 Licence

Ce projet est sous licence **MIT** — utilisation libre et ouverte.

```
MIT License © 2025 Julien Texier
```

---

## 💬 Contact & support

- 📧 [julien.texier@ac-poitiers.fr](mailto:julien.texier@ac-poitiers.fr)  
- 🐙 [GitHub – julientexier86](https://github.com/julientexier86)  
- 🌍 [Site O2switch – instance déployée](https://iyou8383.odns.fr/Publipostage)

---
# PublipostageEvalNat-web
