@echo off
REM Streamlit UI起動スクリプト (Windows)

cd /d "%~dp0"

echo 医学論文管理システム - Streamlit UI
echo ==================================
echo.
echo 起動中...
echo.

streamlit run app\app.py --server.port 8501 --server.headless false

pause
