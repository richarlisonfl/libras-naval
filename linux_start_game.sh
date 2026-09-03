#!/bin/bash

# Caminho base do script (resolvido para caminho absoluto)
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
# Ambiente virtual único do componente Python
VENV_DIR="$BASE_DIR/detection_system/.venv"
REQ_FILE="$BASE_DIR/detection_system/requirements.txt"

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
else
    echo "Ambiente virtual já existe. Pulando criação."
fi

# Ativar ambiente virtual
source "$VENV_DIR/bin/activate"
echo "Ambiente virtual ativado."

###############################################
# 3) Instalar dependências do requirements.txt
###############################################
if [ ! -f "$REQ_FILE" ]; then
    echo "Arquivo requirements.txt não encontrado:"
    echo "$REQ_FILE"
    exit 1
fi

echo "Verificando dependências..."

deps_faltando=false

while IFS= read -r line || [ -n "$line" ]; do
    # Ignorar linhas vazias ou comentários
    [[ -z "$line" || "$line" == \#* ]] && continue
    
    pkg=$(echo "$line" | cut -d'=' -f1)
    ver_esperada="$line"
    ver_instalada=$(python -m pip show "$pkg" 2>/dev/null | grep Version | awk '{print $2}')

    if [ -z "$ver_instalada" ]; then
        echo "Pacote ausente: $pkg"
        deps_faltando=true
    else
        if [ "$line" != "$pkg==$ver_instalada" ]; then
            echo "Versão divergente: $pkg (instalada $ver_instalada, esperado $ver_esperada)"
            deps_faltando=true
        fi
    fi
done < "$REQ_FILE"

if [ "$deps_faltando" = true ]; then
    echo "Instalando/Atualizando dependências..."
    python -m pip install -r "$REQ_FILE" || { echo "Erro ao instalar dependências"; exit 1; }
else
    echo "Todas as dependências já estão satisfeitas."
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
cd "$BASE_DIR/game_server" || { echo "Erro: pasta game não encontrada"; exit 1; }

echo "Iniciando servidor HTTP na porta 3000..."
npm install || { echo "Erro ao instalar dependências do servidor"; exit 1; }
npm start &
SERVER_PID=$!
echo "Servidor HTTP PID: $SERVER_PID"

###############################################
# 5) Iniciar script de reconhecimento
###############################################
cd "$BASE_DIR" || exit 1

echo "Iniciando script de reconhecimento..."
# Use o python do venv para garantir as dependências corretas
if [ -x "$VENV_DIR/bin/python" ]; then
    "$VENV_DIR/bin/python" detection_system/src/reconhecimento_app.py &
    RECON_PID=$!
else
    # fallback para python3.11 do sistema
    python3.11 detection_system/src/reconhecimento_app.py &
    RECON_PID=$!
fi
echo "Reconhecimento PID: $RECON_PID"

echo "Pressione Ctrl+C para encerrar ambos os processos."

wait
