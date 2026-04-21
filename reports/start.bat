@echo off
echo 🚀 Starting PostMortemAI...
docker compose up -d
echo ✅ Running at http://localhost:8000/static/index.html
timeout 3 >nul
start http://localhost:8000/static/index.html