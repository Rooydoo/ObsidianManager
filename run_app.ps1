# Streamlit UI起動スクリプト (PowerShell)

Set-Location $PSScriptRoot

Write-Host "医学論文管理システム - Streamlit UI" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "起動中..." -ForegroundColor Yellow
Write-Host ""

streamlit run app\app.py --server.port 8501 --server.headless false
