#!/usr/bin/env bash
echo "Publipostage EvalNat - Ouverture des brouillons dans Thunderbird..."

# Change de dossier courant pour être dans celui du script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Boucle sur les fichiers eml
for f in eml/*.eml; do
    if [ -f "$f" ]; then
        echo "Ouverture de $f..."
        # Demande à macOS d'ouvrir le fichier, préférentiellement avec Thunderbird
        open -a "Thunderbird" "$f" 2>/dev/null || open "$f"
        # Petite pause pour ne pas tout engorger
        sleep 0.8
    fi
done

echo "Termine ! Vous pouvez fermer cette fnetre."
