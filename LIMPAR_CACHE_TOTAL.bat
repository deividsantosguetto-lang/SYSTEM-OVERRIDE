@echo off
echo ========================================
echo   LIMPEZA TOTAL - GIT E CACHE
echo ========================================
echo.

echo [1/7] Removendo cache local do Git...
git rm -rf --cached .

echo [2/7] Adicionando tudo novamente (limpo)...
git add .

echo [3/7] Verificando status...
git status

echo [4/7] Commit de limpeza...
git commit -m "Clean rebuild: requirements.txt limpo + cache resetado"

echo [5/7] Forcar push (sobrescrever remoto)...
git push origin main --force

echo [6/7] Verificando arquivos enviados...
git ls-files | findstr requirements.txt

echo [7/7] Concluido!
echo.
echo ========================================
echo   CACHE LIMPO E ENVIADO
echo ========================================
echo.
echo Proximos passos:
echo 1. Va para Railway
echo 2. Settings -^> Deletar deploy anterior
echo 3. Clique "Redeploy" para build do zero
echo.
pause
