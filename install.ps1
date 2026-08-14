# install.ps1 - Automated Installation Script (Vierge PC Ready)
param (
    [string]$InstallDir = "$env:LOCALAPPDATA\PVL_Operator_Analyzer"
)

$ErrorActionPreference = "Stop"
$RepoUrl = "https://github.com/Anwar-Brahem/ChatBot/archive/refs/heads/main.zip"
$ZipPath = "$env:TEMP\pvl_app.zip"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   Installing PVL Operator Analyzer       " -ForegroundColor Cyan
Write-Host "   Target: $InstallDir" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Download and Extract Latest Code from GitHub
Write-Host "`n[1/5] Downloading application files from GitHub..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $RepoUrl -OutFile $ZipPath

if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

Expand-Archive -Path $ZipPath -DestinationPath "$env:TEMP\pvl_extracted" -Force

# Détecter si les fichiers sont dans ChatBot-main ou ChatBot-main/PVL_Operator_Analyzer
$ExtractedRoot = "$env:TEMP\pvl_extracted\ChatBot-main"
if (Test-Path "$ExtractedRoot\PVL_Operator_Analyzer") {
    Move-Item -Path "$ExtractedRoot\PVL_Operator_Analyzer\*" -Destination $InstallDir -Force
    if (Test-Path "$ExtractedRoot\PVL.png") {
        Move-Item -Path "$ExtractedRoot\PVL.png" -Destination $InstallDir -Force
    }
} else {
    Move-Item -Path "$ExtractedRoot\*" -Destination $InstallDir -Force
}

Remove-Item -Path $ZipPath -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:TEMP\pvl_extracted" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Check and Auto-Install Python if Missing
Write-Host "`n[2/5] Checking Python installation..." -ForegroundColor Yellow
$PythonCmd = Get-Command "python" -ErrorAction SilentlyContinue

if (-not $PythonCmd) {
    Write-Host "Python not found. Downloading and installing Python 3.11 silently..." -ForegroundColor Yellow
    $PythonInstaller = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe" -OutFile $PythonInstaller
    Start-Process -FilePath $PythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
    Remove-Item -Path $PythonInstaller -Force -ErrorAction SilentlyContinue
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "Python installation detected." -ForegroundColor Green
}

# 3. Create Virtual Environment and Install Dependencies
Write-Host "`n[3/5] Setting up Virtual Environment..." -ForegroundColor Yellow
Set-Location $InstallDir

# Trouver le binaire python fonctionnel
$PythonExe = (Get-Command "python" -ErrorAction SilentlyContinue).Source
if (-not $PythonExe -and (Test-Path "C:\Program Files\Python311\python.exe")) {
    $PythonExe = "C:\Program Files\Python311\python.exe"
}

& $PythonExe -m venv venv
$VenvPip = "$InstallDir\venv\Scripts\pip.exe"

Write-Host "Installing Python requirements..." -ForegroundColor Yellow
& $VenvPip install --upgrade pip
& $VenvPip install -r "$InstallDir\requirements.txt"

# 4. Install Ollama & Configure Model
Write-Host "`n[4/5] Checking Ollama and configuring model..." -ForegroundColor Yellow

# A. Auto-install Ollama if missing
if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama not found. Downloading and installing Ollama..." -ForegroundColor Yellow
    $OllamaSetup = "$env:TEMP\OllamaSetup.exe"
    Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $OllamaSetup
    Start-Process -FilePath $OllamaSetup -ArgumentList "/silent" -Wait
    Remove-Item -Path $OllamaSetup -Force -ErrorAction SilentlyContinue
    
    # Ajouter le chemin standard d'Ollama au PATH actuel
    $OllamaPath = "$env:LOCALAPPDATA\Programs\Ollama"
    if (Test-Path $OllamaPath) {
        $env:Path = "$OllamaPath;" + $env:Path
    }
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "Ollama is already installed." -ForegroundColor Green
}

# B. Configurer le modèle par défaut dans le fichier config
$DefaultsFile = "$InstallDir\config\defaults.py"
if (Test-Path $DefaultsFile) {
    (Get-Content $DefaultsFile) -replace 'OLLAMA_MODEL = .*', 'OLLAMA_MODEL = "gemma4:31b-cloud"' | Set-Content $DefaultsFile
}

$ConfigFile = "$InstallDir\config.py"
if (Test-Path $ConfigFile) {
    (Get-Content $ConfigFile) -replace 'OLLAMA_MODEL = .*', 'OLLAMA_MODEL = "gemma4:31b-cloud"' | Set-Content $ConfigFile
}

# C. Démarrer le serveur Ollama si nécessaire et pull du modèle
Write-Host "Ensuring Ollama server is running..." -ForegroundColor Yellow
$OllamaProcess = Get-Process "ollama" -ErrorAction SilentlyContinue
if (-not $OllamaProcess) {
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 4
}

Write-Host "Pulling model gemma4:31b-cloud (si requis)..." -ForegroundColor Yellow
try {
    ollama pull gemma4:31b-cloud
} catch {
    Write-Host "Note: Téléchargement ignoré ou géré directement par l'API cloud." -ForegroundColor Gray
}

# 5. Create Desktop Shortcut
Write-Host "`n[5/5] Creating Desktop Shortcut..." -ForegroundColor Yellow
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$VenvPythonW = "$InstallDir\venv\Scripts\pythonw.exe"

$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("$DesktopPath\PVL Operator Analyzer.lnk")
$Shortcut.TargetPath = $VenvPythonW
$Shortcut.Arguments = "`"$InstallDir\app.py`""
$Shortcut.WorkingDirectory = $InstallDir
if (Test-Path "$InstallDir\PVL.png") {
    $Shortcut.IconLocation = "$InstallDir\PVL.png"
}
$Shortcut.Save()

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host " Installation Complete! " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
