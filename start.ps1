$ErrorActionPreference = 'Stop'

$baseDir = $PSScriptRoot
$detectionDir = Join-Path $baseDir 'detection_system'
$venvDir = Join-Path $detectionDir '.venv'
$venvPython = Join-Path $venvDir 'Scripts\python.exe'
$requirementsFile = Join-Path $detectionDir 'requirements.txt'
$serverDir = Join-Path $baseDir 'game_server'
$serverProcess = $null
$exitCode = 0

try {
    $nodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
    $npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
    if (-not $nodeCommand -or -not $npmCommand) {
        throw 'Node.js e npm são necessários. Instale Node.js e execute este script novamente.'
    }
    Write-Host "Node.js encontrado: $(& $nodeCommand.Source --version)"
    Write-Host "npm encontrado: $(& $npmCommand.Source --version)"

    $pythonCommand = $null
    $pythonArguments = @()
    $pythonLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($pythonLauncher) {
        & $pythonLauncher.Source -3.11 --version *> $null
        if ($LASTEXITCODE -eq 0) {
            $pythonCommand = $pythonLauncher.Source
            $pythonArguments = @('-3.11')
        }
    }

    if (-not $pythonCommand) {
        $pythonCandidate = Get-Command python.exe -ErrorAction SilentlyContinue
        if ($pythonCandidate) {
            $pythonVersion = & $pythonCandidate.Source -c "import sys; print('%s.%s' % (sys.version_info[0], sys.version_info[1]))" 2>$null
            if ($LASTEXITCODE -eq 0 -and $pythonVersion.Trim() -eq '3.11') {
                $pythonCommand = $pythonCandidate.Source
            }
        }
    }

    if (-not $pythonCommand) {
        throw 'Python 3.11 não encontrado. Instale Python 3.11 e marque a opção de adicionar ao PATH, ou instale o Python Launcher para Windows.'
    }
    Write-Host 'Python 3.11 encontrado.'

    if (-not (Test-Path $venvPython)) {
        Write-Host "Criando ambiente virtual em $venvDir..."
        & $pythonCommand @pythonArguments -m venv $venvDir
        if ($LASTEXITCODE -ne 0) {
            throw 'Erro ao criar o ambiente virtual.'
        }
    }

    if (-not (Test-Path $requirementsFile)) {
        throw "Arquivo requirements.txt não encontrado: $requirementsFile"
    }

    Write-Host 'Instalando/verificando dependências Python...'
    & $venvPython -m pip install -r $requirementsFile
    if ($LASTEXITCODE -ne 0) {
        throw 'Erro ao instalar as dependências Python.'
    }

    Write-Host 'Instalando/verificando dependências do servidor...'
    Push-Location $serverDir
    try {
        & $npmCommand.Source install
        if ($LASTEXITCODE -ne 0) {
            throw 'Erro ao instalar as dependências do servidor.'
        }
    }
    finally {
        Pop-Location
    }

    Write-Host 'Iniciando servidor do jogo na porta 3000...'
    $serverProcess = Start-Process -FilePath $nodeCommand.Source -ArgumentList 'server.js' -WorkingDirectory $serverDir -PassThru
    Write-Host "Servidor iniciado (PID: $($serverProcess.Id)). Pressione Ctrl+C para encerrar."

    Push-Location $baseDir
    try {
        Write-Host 'Iniciando menu principal do sistema...'
        & $venvPython (Join-Path $detectionDir 'main.py')
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}
catch {
    Write-Error $_
    $exitCode = 1
}
finally {
    if ($serverProcess -and -not $serverProcess.HasExited) {
        Write-Host 'Encerrando servidor do jogo...'
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

exit $exitCode