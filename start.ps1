# ============================================================================
# SATO AI Fashion Chatbot - Quick Start Script
# ============================================================================

Write-Host "🚀 Starting SATO AI Fashion Chatbot..." -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Please create a .env file with your GEMINI_API_KEY" -ForegroundColor Yellow
    Write-Host "Example:" -ForegroundColor Gray
    Write-Host "GEMINI_API_KEY=your_api_key_here" -ForegroundColor Gray
    Write-Host ""
    
    $continue = Read-Host "Do you want to continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit
    }
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.8+." -ForegroundColor Red
    exit 1
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js." -ForegroundColor Red
    exit 1
}

# Check if Ollama is running
Write-Host ""
Write-Host "🔍 Checking Ollama status..." -ForegroundColor Cyan
try {
    $ollamaCheck = Invoke-WebRequest -Uri "http://localhost:11434" -Method GET -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Ollama is running" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama not detected. Starting Ollama..." -ForegroundColor Yellow
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
}

# Check if packages are installed
Write-Host ""
Write-Host "📦 Checking dependencies..." -ForegroundColor Cyan

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing Node.js packages..." -ForegroundColor Yellow
    npm install
}

Write-Host ""
Write-Host "🎯 Starting SATO backend server..." -ForegroundColor Cyan
Write-Host "Server will be available at: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the Flask server
python api_server.py
