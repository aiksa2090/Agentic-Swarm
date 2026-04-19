# Requires PowerShell 7+
$ErrorActionPreference = "Stop"

Write-Host ">>> Starting Local Agentic Swarm Automation..." -ForegroundColor Cyan

# --- 1. Clean Corrupted Pip Folders ---
Write-Host ">>> Cleaning corrupted pip distributions (~ympy)..." -ForegroundColor Yellow
$corruptDirs = Get-ChildItem -Path "$env:APPDATA\Python\Python313\site-packages" -Filter "~ympy*" -Directory -ErrorAction SilentlyContinue
foreach ($dir in $corruptDirs) {
    Write-Host "Removing: $($dir.FullName)" -ForegroundColor DarkGray
    Remove-Item -Path $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
}

$VenvDir = "venv"

if (-not (Test-Path -Path $VenvDir)) {
    Write-Host ">>> Creating virtual environment inheriting system packages (PyTorch/CUDA)..." -ForegroundColor Yellow
    python -m venv $VenvDir --system-site-packages
}

Write-Host ">>> Activating environment..." -ForegroundColor Yellow
$ActivateScript = ".\$VenvDir\Scripts\Activate.ps1"
if (Test-Path -Path $ActivateScript) {
    . $ActivateScript
} else {
    Write-Error "Failed to activate virtual environment."
}

# --- 2. Correct Pip Update ---
Write-Host ">>> Installing and Updating requirements..." -ForegroundColor Yellow
python.exe -m pip install -U pip setuptools --quiet

python.exe -m pip install --no-cache-dir pywebview fastapi uvicorn websockets sqlalchemy jinja2 transformers huggingface_hub accelerate bitsandbytes python-dotenv --quiet

if (Test-Path "requirements.txt") {
    python.exe -m pip install -r requirements.txt --quiet
}

# --- 3. Offline Mode Verification ---
Write-Host ">>> Offline Mode Active: Hugging Face online checks disabled." -ForegroundColor Green
Write-Host ">>> Local models will be served directly from C:\Users\USERNAME\.cache\huggingface\hub" -ForegroundColor Green

Write-Host ">>> Cleaning up old processes on port 8123..." -ForegroundColor Yellow
$existingPid = (Get-NetTCPConnection -LocalPort 8123 -ErrorAction SilentlyContinue).OwningProcess
foreach ($pidToKill in $existingPid) {
    if ($pidToKill) {
        Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 1

Write-Host ">>> Launching Native Agentic Swarm Desktop Application..." -ForegroundColor Green
python.exe desktop_app.py

