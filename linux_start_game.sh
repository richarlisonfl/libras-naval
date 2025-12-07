#!/bin/bash

# Caminho base do script
BASE_DIR="$(dirname "$0")"
VENV_DIR="$BASE_DIR/computer_vision/.venv311"
REQ_FILE="$BASE_DIR/computer_vision/requirements.txt"

###############################################
# Instalar Python 3.11 caso não exista
###############################################
instalar_python() {
    echo "Python 3.11 não encontrado. Instalando..."

    sudo apt update || { echo "Erro ao atualizar pacotes"; exit 1; }

    sudo apt install -y software-properties-common build-essential zlib1g-dev \
    libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev \
    libffi-dev libsqlite3-dev wget curl llvm libbz2-dev liblzma-dev tk-dev

    cd /usr/src || exit 1

    sudo wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz
    sudo tar xzf Python-3.11.0.tgz
    cd Python-3.11.0 || exit 1

    sudo ./configure --enable-optimizations
    sudo make -j"$(nproc)"
    sudo make altinstall

    echo "Python 3.11 instalado com sucesso."
}

###############################################
# 1) Verificar Python 3.11
###############################################
if ! command -v python3.11 >/dev/null 2>&1; then
    instalar_python
else
    echo "Python 3.11 encontrado: $(python3.11 --version)"
fi

###############################################
# 2) Criar ambiente virtual com Python 3.11
###############################################
if [ ! -d "$VENV_DIR" ]; then
    echo "Criando ambiente virtual em $VENV_DIR..."
    python3.11 -m venv "$VENV_DIR" || { echo "Erro ao criar venv"; exit 1; }
fi

# Ativar ambiente virtual
source "$VENV_DIR/bin/activate"
echo "Ambiente virtual ativado."

###############################################
# 3) Instalar dependências do requirements.txt
###############################################
if [ ! -f "$REQ_FILE" ]; then
    echo "Arquivo requirements.txt não encontrado em:"
    echo "$REQ_FILE"
    exit 1
fi

echo "Verificando dependências do requirements.txt..."

# Calcula hash das libs instaladas
INSTALLED_HASH="$(pip freeze | sha256sum | awk '{print $1}')"
REQ_HASH="$(sha256sum "$REQ_FILE" | awk '{print $1}')"

if [ "$INSTALLED_HASH" != "$REQ_HASH" ]; then
    echo "Dependências diferentes — Instalando/Atualizando pacotes..."
    pip install -r "$REQ_FILE" || { echo "Erro ao instalar dependências"; exit 1; }
else
    echo "Todas as dependências já estão atualizadas."
fi

###############################################
# Encerramento limpo ao pressionar Ctrl+C
###############################################
cleanup() {
    echo -e "\nEncerrando processos..."

    [ -n "$SERVER_PID" ] && kill "$SERVER_PID" 2>/dev/null
    [ -n "$RECON_PID" ] && kill "$RECON_PID" 2>/dev/null

    echo "Todos os processos foram encerrados."
    exit 0
}

trap cleanup SIGINT

###############################################
# 4) Iniciar servidor HTTP
###############################################
cd "$BASE_DIR/game" || { echo "Erro: pasta game não encontrada"; exit 1; }

echo "Iniciando servidor HTTP na porta 5501..."
python3 -m http.server 5501 &
SERVER_PID=$!
echo "Servidor HTTP PID: $SERVER_PID"

###############################################
# 5) Iniciar script de reconhecimento
###############################################
cd "$BASE_DIR" || exit 1

echo "Iniciando script de reconhecimento..."
python3.11 computer_vision/src/main_reconhecimento_final_adaptado.py &
RECON_PID=$!
echo "Reconhecimento PID: $RECON_PID"

echo "Pressione Ctrl+C para encerrar ambos os processos."

wait
