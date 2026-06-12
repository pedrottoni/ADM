@echo off
echo ========================================================
echo 🚀 Shopee Growth Quest - Inicializando...
echo ========================================================
echo.
echo Verificando dependencias...
python -m pip install -r requirements.txt > nul 2>&1

echo.
echo Iniciando o Dashboard...
echo O navegador deve abrir automaticamente.
echo Pressione Ctrl+C nesta janela para parar o servidor.
echo.
python -m streamlit run dashboard/app.py --server.headless true
pause
