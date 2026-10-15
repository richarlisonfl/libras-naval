#!/usr/bin/env bash
set -Eeuo pipefail

BASE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$BASE_DIR/detection_system/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"
SERVER_DIR="$BASE_DIR/game_server"
NPM_STATE_FILE="$SERVER_DIR/node_modules/.libras-naval-dependencies"

fail() {
    printf 'Erro: %s\n' "$*" >&2
    exit 1
}

[[ -x "$VENV_PYTHON" ]] || fail "Ambiente virtual não encontrado. Execute ./install.sh primeiro."
"$VENV_PYTHON" -c 'import sys; sys.exit(sys.version_info[:2] != (3, 11))' \
    || fail "O ambiente virtual não usa Python 3.11. Execute ./install.sh novamente."
"$VENV_PYTHON" -c 'import cv2, mediapipe, numpy, sklearn, websockets' \
    >/dev/null 2>&1 \
    || fail "Faltam dependências Python no ambiente virtual. Execute ./install.sh novamente."

[[ -f "$BASE_DIR/detection_system/main.py" ]] || fail "Arquivo detection_system/main.py não encontrado."
[[ -f "$SERVER_DIR/server.js" && -f "$SERVER_DIR/package.json" && -f "$SERVER_DIR/package-lock.json" ]] \
    || fail "Arquivos do servidor do jogo não encontrados em $SERVER_DIR."
command -v node >/dev/null 2>&1 || fail "Node.js não encontrado. Execute ./install.sh."
node -e 'process.exit(Number(process.versions.node.split(".")[0]) < 18 ? 1 : 0)' \
    || fail "Node.js 18 ou superior é necessário. Execute ./install.sh."
command -v npm >/dev/null 2>&1 || fail "npm não encontrado. Execute ./install.sh."

NPM_DEPS_HASH="$(sha256sum "$SERVER_DIR/package.json" "$SERVER_DIR/package-lock.json")"
[[ -d "$SERVER_DIR/node_modules/express" ]] \
    && [[ -f "$NPM_STATE_FILE" ]] \
    && [[ "$(cat "$NPM_STATE_FILE")" == "$NPM_DEPS_HASH" ]] \
    && (cd "$SERVER_DIR" && npm ls --depth=0 --silent >/dev/null 2>&1) \
    || fail "Dependências do servidor ausentes ou desatualizadas. Execute ./install.sh."

source "$VENV_DIR/bin/activate"

SERVER_PID=""
cleanup() {
    local status=$?
    trap - EXIT INT TERM
    if [[ -n "$SERVER_PID" ]]; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "Iniciando servidor HTTP na porta 3000..."
(cd "$SERVER_DIR" && exec node server.js) &
SERVER_PID=$!

open_web_page() {
    local url="http://localhost:3000"
    if ! command -v xdg-open >/dev/null 2>&1; then
        printf 'Não foi possível abrir o navegador automaticamente.\n'
        printf 'Acesse manualmente: %s\n' "$url"
        return 1
    fi

    xdg-open "$url" >/dev/null 2>&1 \
        || {
            printf 'Não foi possível abrir o navegador automaticamente.\n'
            printf 'Acesse manualmente: %s\n' "$url"
            return 1
        }
    printf 'Página web aberta em %s\n' "$url"
}

while true; do
    printf '\n'
    printf '%s\n' '================ LibrasNaval ================'
    printf '%s\n' '1. Abrir página web'
    printf '%s\n' '2. Iniciar menu principal do sistema'
    printf '%s\n' '3. Sair'
    read -r -p 'Escolha uma opção: ' opcao

    case "$opcao" in
        1)
            open_web_page || true
            ;;
        2)
            break
            ;;
        3)
            exit 0
            ;;
        *)
            printf 'Opção inválida. Escolha 1, 2 ou 3.\n'
            ;;
    esac
done

echo "Iniciando menu principal do sistema..."
cd "$BASE_DIR"
python detection_system/main.py
