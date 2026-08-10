# install.ps1 - Automated Installation Script for PVL Operator Analyzer
$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/Anwar-Brahem/ChatBot/archive/refs/heads/main.zip"
$InstallDir = "$env:LOCALAPPDATA\PVL_Operator_Analyzer"
$ZipPath = "$env:TEMP\pvl_app.zip"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Installing PVL Operator Analyzer       " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Download and Extract Latest Code from GitHub
Write-Host "`n[1/5] Downloading application files from GitHub..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $RepoUrl -OutFile $ZipPath
if (Test-Path $InstallDir) { Remove-Item -Path $InstallDir -Recurse -Force }
Expand-Archive -Path $ZipPath -DestinationPath $env:TEMP\pvl_extracted -Force
Move-Item -Path "$env:TEMP\pvl_extracted\*" -Destination $InstallDir -Force
Remove-Item -Path $ZipPath -Force
Remove-Item -Path "$env:TEMP\pvl_extracted" -Recurse -Force

# 2. Check Python Installation
Write-Host "`n[2/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonCmd = (Get-Command python -ErrorAction Stop).Source
} catch {
    Write-Host "Error: Python is not installed or not added to PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.10+ from python.org and re-run setup." -ForegroundColor Red
    Pause
    Exit
}

# 3. Create Virtual Environment and Install Dependencies
Write-Host "`n[3/5] Setting up Virtual Environment..." -ForegroundColor Yellow
Set-Location $InstallDir
python -m venv venv
$VenvPython = "$InstallDir\venv\Scripts\python.exe"
$VenvPip = "$InstallDir\venv\Scripts\pip.exe"

Write-Host "Installing Python requirements..." -ForegroundColor Yellow
& $VenvPip install --upgrade pip
& $VenvPip install -r "$InstallDir\requirements.txt"

# 4. Configure Model (Local vs Cloud)
Write-Host "`n[4/5] Model Configuration" -ForegroundColor Yellow
Write-Host "Choose how you want to run Ollama Gemma4 31B:"
Write-Host " [1] Cloud Mode (gemma4:31b-cloud) - Lightweight, requires internet connection"
Write-Host " [2] Local Mode (gemma4:31b) - Downloads model locally via Ollama"
$Choice = Read-Host "Enter choice (1 or 2)"

if ($Choice -eq "2") {
    Write-Host "`nConfiguring Local Mode..." -ForegroundColor Green
    
    # Check if Ollama is installed
    if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) {
        Write-Host "Ollama not found. Downloading Ollama installer..." -ForegroundColor Yellow
        $OllamaSetup = "$env:TEMP\OllamaSetup.exe"
        Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $OllamaSetup
        Start-Process -FilePath $OllamaSetup -Wait
        Remove-Item -Path $OllamaSetup -Force
    }

    Write-Host "Pulling local model gemma4:31b (This may take some time depending on connection)..." -ForegroundColor Yellow
    ollama pull gemma4:31b
    
    # Update config.py
    (Get-Content "$InstallDir\config.py") -replace 'OLLAMA_MODEL = .*', 'OLLAMA_MODEL = "gemma4:31b"' | Set-Content "$InstallDir\config.py"
} else {
    Write-Host "`nConfiguring Cloud Mode..." -ForegroundColor Green
    (Get-Content "$InstallDir\config.py") -replace 'OLLAMA_MODEL = .*', 'OLLAMA_MODEL = "gemma4:31b-cloud"' | Set-Content "$InstallDir\config.py"
}

# 5. Create Desktop Shortcut
Write-Host "`n[5/5] Creating Desktop Shortcut..." -ForegroundColor Yellow
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("$DesktopPath\PVL Operator Analyzer.lnk")
$Shortcut.TargetPath = $VenvPython
$Shortcut.Arguments = "`"$InstallDir\app.py`""
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Save()

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host " Installation Complete! " -ForegroundColor Green
Write-Host " Shortcut created on your Desktop." -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Pause