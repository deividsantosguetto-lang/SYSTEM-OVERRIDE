@echo off
echo ====================================================
echo   PUSH PARA GITHUB - VIRALCUT PRO
echo ====================================================
echo.

echo [1/3] Adicionando arquivos ao Git...
git add .

echo [2/3] Fazendo commit...
git commit -m "Deploy ready: SCALE + Security + Railway config"

echo [3/3] Enviando para GitHub...
git push origin main

echo.
echo ====================================================
echo   CONCLUIDO!
echo ====================================================
echo.
echo Proximos passos:
echo 1. Va para https://railway.app
echo 2. Faca login com GitHub
echo 3. Clique em "Start a New Project"
echo 4. Escolha "Deploy from GitHub repo"
echo 5. Selecione "viralcut-pro"
echo.
pause
