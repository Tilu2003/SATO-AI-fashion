# Fix Corrupted HTML File
# This script replaces the corrupted index.html with the fixed version

Write-Host "🔧 Fixing corrupted index.html..." -ForegroundColor Cyan

$oldFile = "c:\Users\User\OneDrive\Desktop\sato-project\static\index.html"
$fixedFile = "c:\Users\User\OneDrive\Desktop\sato-project\static\index_fixed.html"
$backupFile = "c:\Users\User\OneDrive\Desktop\sato-project\static\index.html.backup"

# Backup old file
if (Test-Path $oldFile) {
    Write-Host "📦 Backing up corrupted file..." -ForegroundColor Yellow
    Copy-Item $oldFile $backupFile -Force
    Write-Host "✅ Backup created: index.html.backup" -ForegroundColor Green
}

# Replace with fixed version
if (Test-Path $fixedFile) {
    Write-Host "🔄 Replacing with fixed version..." -ForegroundColor Yellow
    Remove-Item $oldFile -Force
    Move-Item $fixedFile $oldFile -Force
    Write-Host "✅ index.html has been fixed!" -ForegroundColor Green
} else {
    Write-Host "❌ Fixed file not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Done! Your HTML file is now clean and working." -ForegroundColor Green
Write-Host "The old corrupted file is saved as: index.html.backup" -ForegroundColor Gray
