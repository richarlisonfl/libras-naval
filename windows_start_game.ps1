$ErrorActionPreference = 'Stop'

$baseDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$computerVisionDir = Join-Path $baseDir 'computer_vision'
$venvDir = Join-Path $computerVisionDir '.venv'
$pythonPath = Join-Path $venvDir 'Scripts\python.exe'
$requirementsPath = Join-Path $computerVisionDir 'requirements.txt'
$serverDir = Join-Path $baseDir 'game_server'
$recognitionScript = Join-Path $computerVisionDir 'src\reconhecimento_app.py'

function Get-Python311 {
    $python = Get-Command py -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        & $python.Source -3.11 --version *> $null
        if ($LASTEXITCODE -eq 0) {
            return [pscustomobject]@{
                Executable = $python.Source
                Arguments = @('-3.11')
            }
        }
    }

    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($null -ne $python) {
        $version = & $python.Source --version 2>&1
        if ($version -match '3\.11') {
            return [pscustomobject]@{
                Executable = $python.Source
                Arguments = @()
            }
        }
    }

    throw 'Python 3.11 não encontrado. Instale-o antes de executar este script.'
}

if (-not (Test-Path $requirementsPath)) {
    throw "Arquivo requirements.txt não encontrado: $requirementsPath"
}

if (-not (Test-Path $pythonPath)) {
    $pythonCommand = Get-Python311
    & $pythonCommand.Executable @($pythonCommand.Arguments) -m venv $venvDir
}

if (-not (Test-Path $pythonPath)) {
    throw "Não foi possível criar o ambiente virtual: $venvDir"
}

Write-Host 'Verificando dependências Python...'
& $pythonPath -m pip install -r $requirementsPath
if ($LASTEXITCODE -ne 0) {
    throw 'Erro ao instalar as dependências Python.'
}

Push-Location $serverDir
try {
    & npm.cmd install
    if ($LASTEXITCODE -ne 0) {
        throw 'Erro ao instalar as dependências do servidor.'
    }
}
finally {
    Pop-Location
}

$serverProcess = $null
$recognitionProcess = $null

try {
    Write-Host 'Iniciando servidor HTTP...'
    $serverProcess = Start-Process -FilePath 'npm.cmd' `
        -ArgumentList 'start' `
        -WorkingDirectory $serverDir `
        -PassThru

    $recognitionProcess = Start-Process -FilePath $pythonPath `
        -ArgumentList $recognitionScript `
        -WorkingDirectory $baseDir `
        -PassThru

    Write-Host "Servidor PID: $($serverProcess.Id)"
    Write-Host "Reconhecimento PID: $($recognitionProcess.Id)"
    Write-Host 'Pressione Ctrl+C para encerrar.'

    Wait-Process -Id $recognitionProcess.Id
}
finally {
    if ($null -ne $serverProcess -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force
    }

    if ($null -ne $recognitionProcess -and -not $recognitionProcess.HasExited) {
        Stop-Process -Id $recognitionProcess.Id -Force
    }
}
