@echo off
echo ========================================
echo   RESET GIT COMPLETO - DEPLOY LIMPO
echo ========================================
echo.

echo [1/7] Fazendo backup da pasta .git...
if exist .git_backup rmdir /s /q .git_backup
move .git .git_backup

echo [2/7] Deletando .git local...
if exist .git rmdir /s /q .git

echo [3/7] Inicializando novo repositorio Git...
git init

echo [4/7] Adicionando APENAS arquivos essenciais...
git add requirements.txt
git add Dockerfile
git add nixpacks.toml
git add Procfile
git add .dockerignore
git add .gitignore
git add servidor_flask.py
git add worker.py
git add database.py
git add tasks.py
git add motor.py
git add automacao_gemini.py
git add templates/

echo [5/7] Commit inicial...
git commit -m "Deploy limpo: estrutura minimal"

echo [6/7] Conectando ao GitHub...
git remote add origin https://github.com/deividsantosguetto-lang/SYSTEM-OVERRIDE.git
git branch -M main

echo [7/7] Push forcado (limpa checksum)...
git push -u origin main --force

echo.
echo ========================================
echo   REPOSITORIO RESETADO!
echo ========================================
echo.
echo Proximo passo:
echo 1. Va para Railway
echo 2. Delete o servico web anterior
echo 3. Crie novo: Deploy from GitHub
echo 4. Selecione SYSTEM-OVERRIDE
echo.
pause
