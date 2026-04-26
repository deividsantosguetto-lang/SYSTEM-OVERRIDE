@echo off
echo ========================================
echo    ATIVANDO OVERRIDE.AI (STREAMLIT)
echo ========================================
echo.
echo Iniciando servidor...
echo Aguarde a pagina abrir automaticamente
echo.
cd /d "%~dp0"
streamlit run app_web.py
pause
