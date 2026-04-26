@echo off
echo ========================================
echo   PREPARANDO DEPLOY - VIRALCUT PRO
echo ========================================
echo.

echo [1/5] Verificando Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Git nao encontrado! Instale em: https://git-scm.com/
    pause
    exit /b 1
)

echo [2/5] Inicializando repositorio Git...
if not exist .git (
    git init
    echo Git inicializado!
) else (
    echo Git ja inicializado.
)

echo [3/5] Adicionando arquivos...
git add .

echo [4/5] Fazendo commit...
git commit -m "Deploy: SCALE feature + Security hardening"

echo [5/5] Proximo passo:
echo.
echo 1. Crie um repositorio no GitHub: https://github.com/new
echo 2. Execute este comando (substitua SEU_USUARIO):
echo    git remote add origin https://github.com/SEU_USUARIO/viralcut-pro.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Depois va para Railway ou Render e conecte seu repositorio!
echo    - Railway: https://railway.app
echo    - Render: https://render.com
echo.
pause
