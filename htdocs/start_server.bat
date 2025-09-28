@echo off
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting AI Health Chatbot Server...
python run_server.py

pause
