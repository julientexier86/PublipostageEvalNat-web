# Mode d'emploi — Publipostage ÉvalNat

Ce guide décrit le flux complet : préparer les exports, générer les documents, vérifier les destinataires et envoyer les résultats. L’application ne transmet aucun courriel elle-même : elle produit des brouillons `.eml` et une archive de contrôle.

## 1. Avant de commencer

Préparez deux fichiers pour **une seule classe** :

1. Le PDF global de restitution ÉvalNat. Il peut contenir plusieurs élèves et plusieurs pages par élève.
2. L’export CSV SIECLE avec les nom, prénom et adresses électroniques des représentants légaux.

Conservez les fichiers originaux dans un emplacement sécurisé. L’application n’est pas un espace d’archivage : les fichiers de traitement sont supprimés après le téléchargement de l’archive.

### Le PDF ÉvalNat

Téléchargez le document destiné aux élèves et à leurs représentants légaux depuis le portail de restitution. L’application reconnaît les mentions de type :

```text
Nom : DUPONT  Prénom : Alice  Classe : 6A
```

Le PDF peut réunir plusieurs disciplines. Les pages portant le même nom, prénom, classe et discipline sont rassemblées dans un seul document final.

### Le CSV SIECLE

Dans SIECLE, utilisez une extraction personnalisée incluant a minima :

- le nom de l’élève ;
- le prénom de l’élève ;
- une ou plusieurs colonnes contenant les courriels des responsables.

Le séparateur habituel `;` est pris en charge. Les encodages UTF-8 et Latin-1 sont normalisés automatiquement. Les colonnes contenant `mail`, `e-mail` ou `courriel` sont détectées.

## 2. Générer le publipostage

1. Ouvrez l’application.
2. Déposez le **PDF ÉvalNat** dans le premier emplacement.
3. Déposez l’**export SIECLE CSV** dans le second.
4. Renseignez l’année scolaire et la classe.
5. Laissez cochée l’option **Créer les brouillons .eml** pour produire un message par document élève.
6. Saisissez, si nécessaire, le message qui sera placé dans chaque brouillon.
7. Cliquez sur **Préparer mon publipostage**.

L’application analyse le PDF, découpe et regroupe les pages, rapproche les élèves du CSV, génère les brouillons et prépare une archive ZIP.

## 3. Choisir les options

### Brouillons `.eml`

Cette option produit un fichier `.eml` par document élève. Le champ destinataire est rempli avec les adresses trouvées dans le CSV. Chaque brouillon contient le PDF correspondant en pièce jointe.

Un document sans adresse trouvée produit malgré tout un brouillon, mais son champ destinataire est vide. Il doit être vérifié avant tout envoi.

### Conserver un PDF unique

Cette option est utile pour vérifier le document source ou si vous ne souhaitez pas de publipostage. Le PDF est copié tel quel dans l’archive ; aucun brouillon `.eml` n’est créé.

### OCR

L’OCR n’est utile que pour un PDF scanné, dont le texte ne peut pas être sélectionné. L’application détecte automatiquement l’absence de texte ; vous pouvez aussi cocher **Forcer l’OCR**.

Le fonctionnement est le suivant :

1. Le moteur OCR local (`ocrmypdf` et Tesseract) est utilisé en priorité.
2. Si ce moteur est indisponible ou échoue, l’application utilise le module OCR externe configuré par l’établissement via `OCR_REMOTE_URL`.
3. Avec `OCR_FORCE_REMOTE=1`, le service externe est utilisé immédiatement.

Ne configurez le module externe que s’il est sous contrôle de l’établissement ou du prestataire autorisé à traiter ces données. Le service doit accepter un PDF multipart et renvoyer un PDF OCRisé.

## 4. Vérifier l'archive avant envoi

Téléchargez l’archive immédiatement : le lien expire au bout de 30 minutes. Elle contient généralement :

```text
Publipostage_6A_2025-2026.zip
├── 6A_DUPONT_Alice_Francais_2025-2026.pdf
├── eml/
│   └── 6A_DUPONT_Alice_Francais_2025-2026.eml
├── parents_source.csv
├── rapport_publipostage.csv
├── _Ouvrir_Dans_Thunderbird.command
└── _Ouvrir_Dans_Thunderbird.bat
```

Ouvrez d’abord `rapport_publipostage.csv` dans LibreOffice ou Excel. Vérifiez particulièrement les lignes dont le statut est `adresse introuvable`.

| Statut | Signification | Action à effectuer |
| --- | --- | --- |
| `prêt à envoyer` | Une ou plusieurs adresses ont été associées. | Contrôler rapidement le destinataire et la pièce jointe. |
| `adresse introuvable` | Aucun courriel n’a été rapproché. | Corriger le CSV ou compléter le brouillon manuellement. |
| Fichier commençant par `INCONNU` | Le nom de l’élève n’a pas été lu dans le PDF. | Vérifier le PDF ; relancer avec OCR si c’est un scan. |

## 5. Ouvrir et envoyer les brouillons

### Thunderbird

Décompressez l’archive, puis utilisez le script d’ouverture correspondant à votre système ou glissez les fichiers `.eml` dans le dossier **Brouillons** de Thunderbird.

Ouvrez chaque brouillon, vérifiez :

- le ou les destinataires ;
- le nom de l’élève dans le sujet ;
- la pièce jointe PDF ;
- le texte du message.

Envoyez seulement après cette vérification.

### Outlook et Apple Mail

Les fichiers `.eml` peuvent être ouverts par double-clic ou importés dans les brouillons selon la version du logiciel. Vérifiez le comportement sur un premier message de test avant une campagne complète.

### Webmails

Les webmails n’importent généralement pas les fichiers `.eml` comme brouillons. Pour Zimbra, utilisez l’archive dédiée décrite ci-dessous.

### Zimbra

Lorsque les brouillons `.eml` sont activés, l’archive ZIP contient aussi `zimbra_publipostage_evalnat.tgz`. Cette archive est conçue pour l’import de messages Zimbra ; elle ne contient aucun mot de passe ni paramètre de connexion.

1. Décompressez d’abord l’archive ZIP téléchargée.
2. Dans Zimbra, créez un dossier dédié, par exemple **Publipostage ÉvalNat**.
3. Dans l’interface Modern, faites un clic droit sur ce dossier puis choisissez **Importer**. Dans l’interface Classic, utilisez **Préférences → Importer/Exporter**.
4. Sélectionnez `zimbra_publipostage_evalnat.tgz` et importez-le dans le dossier dédié.
5. Ouvrez un premier message de contrôle ; selon la version de Zimbra, placez-le dans Brouillons ou utilisez **Modifier comme nouveau** avant l’envoi.

Cette méthode est la plus sûre car Zimbra gère l’authentification lui-même. Pour une intégration créant directement de vrais brouillons dans une boîte Zimbra, il faudrait ensuite configurer l’API Zimbra `SaveDraftRequest` avec une authentification de l’établissement ; ce n’est pas activé par défaut afin de ne jamais demander ni conserver les identifiants de messagerie.

## 6. Configuration technique

### Installation locale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

L’application est alors disponible sur `http://127.0.0.1:8000`.

### OCR externe de secours

Définissez ces variables dans l’environnement de l’application, jamais dans le dépôt Git :

```bash
export OCR_REMOTE_URL="https://ocr.mon-etablissement.fr/ocr"
export OCR_REMOTE_TOKEN="jeton-secret-optionnel"
# Optionnel : force le secours externe, par exemple si le serveur local est sous-dimensionné
export OCR_FORCE_REMOTE=1
```

Le service est appelé avec le champ de formulaire `pdf`, ainsi que `lang` et `profile`. Il doit retourner le PDF résultant directement dans la réponse HTTP avec un code `200`.

### Performances

- Le PDF est lu une seule fois avec PyMuPDF.
- Les pages sont regroupées avant l’écriture des fichiers finaux.
- Évitez de traiter plusieurs classes dans le même PDF.
- Pour un scan volumineux, utilisez le profil OCR **Rapide** ou le module externe dimensionné pour ce service.

## 7. Résolution des problèmes

### Aucun destinataire n'est trouvé

Vérifiez les intitulés des colonnes du CSV et la présence réelle des adresses. Vérifiez aussi l’orthographe des noms dans le PDF : les accents, les tirets et les espaces sont normalisés, mais un prénom différent reste une correspondance différente.

### Des fichiers `INCONNU` sont créés

Le PDF ne contient pas l’en-tête attendu ou son texte n’est pas exploitable. Activez l’OCR. Si le problème persiste, conservez une page PDF exemple (anonymisée) afin d’adapter le détecteur à ce format de restitution.

### L'OCR échoue

Installez `ocrmypdf` et les langues Tesseract nécessaires sur le serveur, ou vérifiez la disponibilité, l’URL et le jeton du module OCR externe.

### Le téléchargement indique que le lien a expiré

Relancez le traitement : les archives sont volontairement supprimées après 30 minutes et dès qu’elles sont téléchargées.

## 8. Bonnes pratiques

- Traitez une classe à la fois.
- Vérifiez systématiquement `rapport_publipostage.csv` avant l’envoi.
- Faites un essai avec un élève volontaire lors de chaque rentrée.
- Ne transmettez jamais l’archive ZIP par un canal non autorisé.
- Gardez le CSV SIECLE et le PDF source dans les emplacements sécurisés prévus par l’établissement.
