@echo off
echo Publipostage EvalNat - Ouverture des brouillons dans Thunderbird...
echo.

:: Boucle sur tous les fichiers .eml du dossier eml/
for %%f in ("eml\*.eml") do (
    echo Ouverture de %%f...
    start "" "%%f"
    :: Pause d'1 seconde pour éviter de surcharger Thunderbird
    timeout /t 1 /nobreak >nul
)

echo.
echo Termine ! Tous les brouillons ont ete ouverts.
pause
