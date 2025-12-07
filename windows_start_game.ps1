@echo off
setlocal enabledelayedexpansion

:: ================================
:: Caminho base
:: ================================
set "BASE_DIR=%~dp0"
set "VENV_DIR=%BASE_DIR%computer_vision\.venv311"
set "REQ_FILE=%BASE_DIR%computer_vision\requirements.txt"

:: ================================
:: Função para checar Python 3.11
:: ================================
python --version 2>nul | findstr "3.11" >nul
if %errorlevel% neq 0 (
    echo Python 3.11 nao encontrado.
    echo Por favor instale Python 3.11 manualmente de https://www.python.org/downloads/windows/
    pause
    exit /b 1
) else (
    for /f "tokens=2 delims= " %%a in ('python --version') do set "PY_VER=%%a"
    echo Python encontrado: %PY_VER%
)

:: ================================
:: Criar ambiente virtual
:: ================================
if not exist "%VENV_DIR%" (
    echo Criando ambiente virtual em %VENV_DIR%...
    python -m venv "%VENV_DIR%" || (
        echo Erro ao criar ambiente virtual
        exit /b 1
    )
) else (
    echo Ambiente virtual ja existe. Pulando criacao.
)

:: ================================
:: Ativar ambiente virtual
:: ================================
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo Erro ao ativar ambiente virtual
    exit /b 1
)
echo Ambiente virtual ativado.

:: ================================
:: Instalar dependencias
:: ================================
if not exist "%REQ_FILE%" (
    echo Arquivo requirements.txt nao encontrado:
    echo %REQ_FILE%
    exit /b 1
)

echo Verificando dependencias...

set "DEPS_FALTANDO=false"
for /f "usebackq tokens=*" %%L in ("%REQ_FILE%") do (
    set "line=%%L"
    :: Ignorar comentarios e linhas vazias
    if not "!line!"=="" if "!line:~0,1!" neq "#" (
        for /f "tokens=1 delims==" %%P in ("!line!") do set "pkg=%%P"
        for /f "tokens=2 delims==" %%V in ("!line!") do set "ver_esperada=%%V"
        
        :: Verifica se o pacote esta instalado
        pip show "!pkg!" >nul 2>&1
        if %errorlevel% neq 0 (
            echo Pacote ausente: !pkg!
            set "DEPS_FALTANDO=true"
        ) else (
            for /f "tokens=2 delims=: " %%I in ('pip show "!pkg!" ^| findstr Version') do set "ver_instalada=%%I"
            if not "!ver_instalada!"=="!ver_esperada!" (
                echo Versao divergente: !pkg! (instalada !ver_instalada!, esperado !ver_esperada!)
                set "DEPS_FALTANDO=true"
            )
        )
    )
)

if "!DEPS_FALTANDO!"=="true" (
    echo Instalando/Atualizando dependencias...
    pip install -r "%REQ_FILE%" || (
        echo Erro ao instalar dependencias
        exit /b 1
    )
) else (
    echo Todas as dependencias ja estao satisfeitas.
)

:: ================================
:: Iniciar servidor HTTP
:: ================================
pushd "%BASE_DIR%game" || (
    echo Erro: pasta game nao encontrada
    exit /b 1
)
echo Iniciando servidor HTTP na porta 5501...
start "" cmd /c "npm install && npm start server.js"
popd

:: ================================
:: Iniciar script de reconhecimento
:: ================================
pushd "%BASE_DIR%" || exit /b 1
echo Iniciando script de reconhecimento...
start "" python computer_vision\src\main_reconhecimento_final_adaptado.py
popd

echo Ambos os processos iniciados. Feche as janelas para encerrar.
pause
