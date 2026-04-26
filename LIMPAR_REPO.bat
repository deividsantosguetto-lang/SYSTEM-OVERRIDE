@echo off
echo ========================================
echo   LIMPANDO ARQUIVOS GRANDES DO GIT
echo ========================================
echo.

echo [1/5] Removendo arquivos Redis do Git...
git rm -r --cached redis-x64-3.0.504/ 2>nul
git rm -r --cached redis-x64-5.0.14.1/ 2>nul
git rm --cached redis.zip 2>nul
git rm --cached redis5.zip 2>nul

echo [2/5] Removendo videos do Git...
git rm -r --cached estoque/ 2>nul
git rm -r --cached cortes/ 2>nul
git rm --cached *.mp4 2>nul

echo [3/5] Commit das alteracoes...
git add .gitignore
git commit -m "Remove arquivos grandes (Redis binaries e videos)"

echo [4/5] Push para GitHub...
git push origin main --force

echo [5/5] Concluido!
echo.
echo ========================================
echo   REPOSITORIO LIMPO!
echo ========================================
echo.
echo Agora volte ao Railway e clique em:
echo "Deployments" -^> "Redeploy"
echo.
pause
