@echo off
title ViralCut Pro - Launcher (Full Stack)
color 0A

echo ===================================================
echo     INICIANDO VIRALCUT PRO (AUTO REDIS)
echo ===================================================
echo.

echo [1/3] Iniciando Redis Portatil (v5.0)...
if exist "redis-x64-5.0.14.1\redis-server.exe" (
    start "ViralCut - REDIS" /min "redis-x64-5.0.14.1\redis-server.exe"
    echo    > Redis iniciado em janela minimizada.
) else (
    echo    [ALERTA] Redis portatil nao encontrado! Certifique-se de que ele esta instalado.
)
timeout /t 3 >nul

echo.
echo [2/3] Iniciando Servidor Web...
start "ViralCut - SITE" cmd /k "python run_production.py"

echo.
echo [3/3] Iniciando Worker...
start "ViralCut - WORKER" cmd /k "python worker.py"

echo.
echo ===================================================
echo     TUDO PRONTO!
echo     Acesse: http://localhost:5000
echo ===================================================
pause
