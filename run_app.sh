#!/bin/bash
# Streamlit UI起動スクリプト (Linux/Mac)

cd "$(dirname "$0")"

echo "医学論文管理システム - Streamlit UI"
echo "=================================="
echo ""
echo "起動中..."
echo ""

streamlit run app/app.py --server.port 8501 --server.headless false
