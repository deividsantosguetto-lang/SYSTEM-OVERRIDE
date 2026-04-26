@echo off
title ViralCut Pro - Launcher
color 0A

echo ===================================================
echo     INICIANDO VIRALCUT PRO (LOCAL MODE)
echo ===================================================
echo.
echo [1/3] Verificando Redis...
echo (Certifique-se de que o Redis ja esta rodando em outra janela ou como servico!)
timeout /t 3

echo.
echo [2/3] Iniciando Servidor Web (Flask)...
start "ViralCut - SITE" cmd /k "python run_production.py"

echo.
echo [3/3] Iniciando Worker (Processamento)...
start "ViralCut - WORKER" cmd /k "python worker.py"

echo.
echo ===================================================
echo     SISTEMA INICIADO!
echo     Acesse: http://localhost:5000
echo ===================================================
pause
