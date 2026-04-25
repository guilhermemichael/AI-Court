param(
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$SkipInstall,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

if ($BackendOnly -and $FrontendOnly) {
    throw "Use apenas um entre -BackendOnly e -FrontendOnly."
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$venvDir = Join-Path $repoRoot ".venv"
$pythonExe = Join-Path $venvDir "Scripts\\python.exe"
$pipExe = Join-Path $venvDir "Scripts\\pip.exe"
$backendEnvLocal = Join-Path $backendDir ".env.local"
$backendEnvTemplate = Join-Path $backendDir ".env.local.example"
$backendUrl = "http://127.0.0.1:8000/health"
$frontendUrl = "http://localhost:5173"

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Test-CommandAvailable([string]$CommandName) {
    return $null -ne (Get-Command $CommandName -ErrorAction SilentlyContinue)
}

function Test-Url([string]$Url) {
    try {
        & $pythonExe -c "import sys, urllib.request; urllib.request.urlopen(sys.argv[1], timeout=2).read()" $Url 2>$null | Out-Null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

function Wait-ForUrl([string]$Url, [int]$Seconds = 30) {
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Url $Url) {
            return $true
        }
        Start-Sleep -Seconds 1
    }
    return $false
}

function Start-Window([string]$WorkingDirectory, [string]$Command) {
    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "Set-Location '$WorkingDirectory'; $Command"
    ) | Out-Null
}

if (-not (Test-Path $venvDir)) {
    Write-Step "Criando .venv local"
    if (Test-CommandAvailable "py") {
        & py -3 -m venv $venvDir
    }
    elseif (Test-CommandAvailable "python") {
        & python -m venv $venvDir
    }
    else {
        throw "Python nao encontrado. Instale Python 3.12+ primeiro."
    }
}

if (-not (Test-Path $pythonExe)) {
    throw "Nao encontrei $pythonExe."
}

if (-not (Test-Path $backendEnvLocal)) {
    Write-Step "Criando backend/.env.local a partir do template local"
    Copy-Item $backendEnvTemplate $backendEnvLocal
}

New-Item -ItemType Directory -Force -Path (Join-Path $backendDir "storage") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $backendDir "storage\\pdfs") | Out-Null

if (-not $SkipInstall) {
    Write-Step "Instalando dependencias do backend na .venv"
    & $pipExe install -e "$repoRoot\\backend[dev]"

    if (-not $BackendOnly) {
        Write-Step "Instalando dependencias do frontend"
        Push-Location $frontendDir
        try {
            npm install
        }
        finally {
            Pop-Location
        }
    }
}

if (-not $FrontendOnly) {
    if (Test-Url $backendUrl) {
        Write-Step "Backend ja esta respondendo em http://127.0.0.1:8000"
    }
    else {
        Write-Step "Abrindo backend em nova janela"
        Start-Window $backendDir "& '$pythonExe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
        if (-not (Wait-ForUrl $backendUrl 45)) {
            throw "Backend nao respondeu em 45 segundos."
        }
    }
}

if (-not $BackendOnly) {
    Write-Step "Abrindo frontend em nova janela"
    Start-Window $frontendDir "npm run dev"
}

if (-not $NoBrowser) {
    Start-Sleep -Seconds 2
    if ($BackendOnly) {
        Start-Process "http://127.0.0.1:8000/docs"
    }
    elseif ($FrontendOnly) {
        Start-Process $frontendUrl
    }
    else {
        Start-Process $frontendUrl
    }
}

Write-Host ""
Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Swagger:  http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
