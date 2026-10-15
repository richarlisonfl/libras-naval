#!/usr/bin/env bash
set -Eeuo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BASE_DIR/detection_system/.venv"
REQ_FILE="$BASE_DIR/detection_system/requirements.txt"
SERVER_DIR="$BASE_DIR/game_server"
SUDO=()

fail() {
    printf 'Erro: %s\n' "$*" >&2
    exit 1
}

[[ -r /etc/os-release ]] || fail "Não foi possível identificar a distribuição Linux."
source /etc/os-release
case " ${ID:-} ${ID_LIKE:-} " in
    *" debian "*|*" ubuntu "*) ;;
    *) fail "A instalação automática oferece suporte a Ubuntu e Debian." ;;
esac

command -v apt-get >/dev/null 2>&1 || fail "apt-get não encontrado."
(( EUID != 0 )) || fail "Execute ./install.sh como usuário normal, não como root."
command -v sudo >/dev/null 2>&1 || fail "A instalação requer sudo."
SUDO=(sudo)

[[ -f "$REQ_FILE" ]] || fail "Arquivo requirements.txt não encontrado: $REQ_FILE"
[[ -f "$SERVER_DIR/package.json" && -f "$SERVER_DIR/package-lock.json" ]] \
    || fail "Arquivos package.json/package-lock.json não encontrados em $SERVER_DIR."

apt_install() {
    "${SUDO[@]}" apt-get install -y "$@"
}

python311_is_usable() {
    local candidate
    for candidate in "$(command -v python3.11 || true)" /usr/bin/python3.11 /usr/local/bin/python3.11; do
        [[ -n "$candidate" && -x "$candidate" ]] || continue
        if "$candidate" -c 'import sys, ssl, zlib; sys.exit(sys.version_info[:2] != (3, 11))' \
            >/dev/null 2>&1; then
            PYTHON_BIN="$candidate"
            return 0
        fi
    done
    return 1
}

ensure_python311() {
    if python311_is_usable; then
        return
    fi

    echo "Preparando Python 3.11..."
    "${SUDO[@]}" apt-get update
    apt_install ca-certificates curl gnupg

    if ! apt_install python3.11 python3.11-venv || ! python311_is_usable; then
        echo "Python 3.11 não está disponível como pacote. Compilando a versão estável mais recente..."
        apt_install build-essential pkg-config libssl-dev zlib1g-dev libncursesw5-dev \
            libreadline-dev libsqlite3-dev libffi-dev libbz2-dev liblzma-dev \
            libgdbm-dev libnss3-dev tk-dev uuid-dev libdb-dev

        (
            set -Eeuo pipefail
            BUILD_DIR="$(mktemp -d)"
            trap 'rm -rf -- "$BUILD_DIR"' EXIT
            VERSION_INDEX="$(curl -fsSL https://www.python.org/ftp/python/)" \
                || fail "Não foi possível consultar as versões oficiais do Python."
            PYTHON_VERSION="$(
                printf '%s\n' "$VERSION_INDEX" \
                    | grep -oE '3\.11\.[0-9]+/' \
                    | tr -d '/' \
                    | sort -Vu \
                    | tail -n 1
            )"
            [[ -n "$PYTHON_VERSION" ]] || fail "Não foi possível encontrar uma versão estável do Python 3.11."
            curl -fL "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz" \
                -o "$BUILD_DIR/Python-$PYTHON_VERSION.tgz"
            tar -xzf "$BUILD_DIR/Python-$PYTHON_VERSION.tgz" -C "$BUILD_DIR"
            cd "$BUILD_DIR/Python-$PYTHON_VERSION"
            ./configure --prefix=/usr/local --with-ensurepip=install
            make -j"$(nproc)"
            "${SUDO[@]}" make altinstall
        ) || fail "Falha ao compilar Python 3.11 a partir do código-fonte oficial."
    fi

    python311_is_usable || fail "Python 3.11 precisa dos módulos ssl e zlib."
}

node_is_usable() {
    command -v node >/dev/null 2>&1 \
        && command -v npm >/dev/null 2>&1 \
        && node -e 'process.exit(Number(process.versions.node.split(".")[0]) < 18 ? 1 : 0)' \
        >/dev/null 2>&1
}

ensure_node() {
    if node_is_usable; then
        return
    fi

    echo "Configurando o repositório oficial NodeSource para Node.js 22..."
    apt_install ca-certificates curl gnupg
    "${SUDO[@]}" install -d -m 0755 /etc/apt/keyrings
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key \
        | "${SUDO[@]}" gpg --dearmor --yes -o /etc/apt/keyrings/nodesource.gpg
    "${SUDO[@]}" chmod 0644 /etc/apt/keyrings/nodesource.gpg
    printf '%s\n' \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_22.x nodistro main" \
        | "${SUDO[@]}" tee /etc/apt/sources.list.d/nodesource.list >/dev/null
    "${SUDO[@]}" apt-get update
    apt_install nodejs
    node_is_usable || fail "Não foi possível instalar Node.js 18 ou superior e npm."
}

ensure_python_runtime_libraries() {
    local package
    local missing=()
    for package in libgl1 libglib2.0-0; do
        if [[ "$("${SUDO[@]}" dpkg-query -W -f='${db:Status-Status}' "$package" 2>/dev/null || true)" != "installed" ]]; then
            missing+=("$package")
        fi
    done
    if (( ${#missing[@]} > 0 )); then
        echo "Instalando bibliotecas de sistema necessárias para OpenCV..."
        apt_install "${missing[@]}"
    fi
}

ensure_venv_support() {
    local test_dir
    test_dir="$(mktemp -d)"
    if "$PYTHON_BIN" -m venv "$test_dir/venv" >/dev/null 2>&1; then
        rm -rf -- "$test_dir"
        return
    fi
    rm -rf -- "$test_dir"

    echo "Instalando o suporte a ambientes virtuais do Python..."
    apt_install python3.11-venv \
        || fail "Não foi possível instalar python3.11-venv. Verifique os repositórios da distribuição."
    test_dir="$(mktemp -d)"
    if ! "$PYTHON_BIN" -m venv "$test_dir/venv" >/dev/null 2>&1; then
        rm -rf -- "$test_dir"
        fail "Python 3.11 não conseguiu criar um ambiente virtual."
    fi
    rm -rf -- "$test_dir"
}

ensure_python311
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3.11)}"
echo "Python: $("$PYTHON_BIN" --version 2>&1)"
ensure_node
echo "Node.js: $(node --version); npm: $(npm --version)"
ensure_python_runtime_libraries
ensure_venv_support

if [[ ! -x "$VENV_DIR/bin/python" ]] \
    || ! "$VENV_DIR/bin/python" -c 'import sys, pip; sys.exit(sys.version_info[:2] != (3, 11))' \
        >/dev/null 2>&1; then
    if [[ -e "$VENV_DIR" || -L "$VENV_DIR" ]]; then
        echo "Ambiente virtual incompleto ou incompatível. Recriando..."
        rm -rf -- "$VENV_DIR"
    else
        echo "Criando ambiente virtual em $VENV_DIR..."
    fi
    "$PYTHON_BIN" -m venv "$VENV_DIR" \
        || fail "Não foi possível criar o ambiente virtual do projeto."
fi

echo "Instalando dependências Python no ambiente virtual..."
"$VENV_DIR/bin/python" -m pip install --disable-pip-version-check -r "$REQ_FILE" \
    || fail "Erro ao instalar dependências Python."

NPM_STATE_FILE="$SERVER_DIR/node_modules/.libras-naval-dependencies"
NPM_DEPS_HASH="$(sha256sum "$SERVER_DIR/package.json" "$SERVER_DIR/package-lock.json")"
if [[ ! -d "$SERVER_DIR/node_modules/express" ]] \
    || [[ ! -f "$NPM_STATE_FILE" ]] \
    || [[ "$(cat "$NPM_STATE_FILE")" != "$NPM_DEPS_HASH" ]] \
    || ! (cd "$SERVER_DIR" && npm ls --depth=0 --silent >/dev/null 2>&1); then
    echo "Instalando dependências Node do servidor..."
    (cd "$SERVER_DIR" && npm ci) || fail "Erro ao instalar dependências Node."
    printf '%s\n' "$NPM_DEPS_HASH" > "$NPM_STATE_FILE"
fi

echo "Instalação concluída. Execute ./start.sh para iniciar o jogo."
