# Kortex Multi-Process Starter
# Runs both Backend and Frontend concurrently

Write-Host "⚡ Starting Kortex Ecosystem..." -ForegroundColor Cyan

# Start Backend
Write-Host "📡 Launching Backend API on http://localhost:8000" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn backend.main:app --port 8000 --reload"

# Start Frontend
Write-Host "🎨 Launching Frontend on http://localhost:5173" -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "🚀 Kortex is running! Close the new windows to stop processes." -ForegroundColor Yellow
