@echo off
echo ========================================
echo  LIMPANDO CACHE GIT - PASTAS PESADAS
echo ========================================
echo.

echo [1/8] Removendo cortes/ do Git...
git rm -r --cached cortes

echo [2/8] Removendo debug_frames/ do Git...
git rm -r --cached debug_frames

echo [3/8] Removendo debug_cortes/ do Git...
git rm -r --cached debug_cortes

echo [4/8] Removendo estoque/ do Git...
git rm -r --cached estoque

echo [5/8] Removendo ffmpeg_extracted/ do Git...
git rm -r --cached ffmpeg_extracted

echo [6/8] Removendo uploads/ do Git...
git rm -r --cached uploads

echo [7/8] Removendo logs/ do Git...
git rm -r --cached logs

echo [8/8] Commit das alteracoes...
git add .dockerignore
git commit -m "Remover pastas pesadas do Git cache"

echo.
echo ========================================
echo   CONCLUIDO!
echo ========================================
echo.
echo Agora execute: git push origin main --force
echo.
pause
