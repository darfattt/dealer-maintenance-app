@echo off
echo Starting Admin Panel with localhost backend connection...
cd admin_panel
set BACKEND_URL=http://localhost:8000
streamlit run admin_app.py --server.port 8503
pause
