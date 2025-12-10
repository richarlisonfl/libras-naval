import { apiGet, apiPost } from "./api.js";

const WS_URL = 'ws://localhost:8765';
let ws = null;
let reconnectInterval = 1000; // 1s
let coluna = undefined, linha = undefined, acao = undefined;

const linhas = 5;
const colunas = ["A", "E", "I", "O", "U"];
let navios = [];
let nickname = 'bito'

async function carregarMapa() {
    try {
        let resposta = await fetch("mapa.json");
        let dados = await resposta.json();
        navios = dados.navios;
    } catch (erro) {
        alert("Erro ao carregar o mapa.");
    }
}

function handleMessage(message){
    const numeros = [1, 2, 3, 4, 5];
    const acoes = ['ok'];

    if (['a', 'e', 'i', 'o', 'u'].some((v) => v === message))
    {
        coluna = message;
    } else if ([1, 2, 3, 4, 5].some((v) => v == message))
    {
        linha = message;
    } else if (['ok', 'limpar'].some((v) => v === message))
    {
        acao = message;
    }

    if (message === 'limpar')
    {
        coluna = undefined;
        linha = undefined;
        acao = undefined;
        return;
    }

    if (message === 'salvar')
    {
        let cells = [];
        for (let linha = 1; linha <= linhas; linha++) {
            for (let coluna of colunas) {
                let id = `cell-${linha}-${coluna}`;
                let cell = document.getElementById(id);
                if (cell) {
                    const navio = navios.includes(id);
                    const estado = cell.classList.value;
                    let estadoId;
                    
                    if (estado === 'acerto' || estado === 'erro')
                        estadoId = 1;
                    else 
                        estadoId = 2;
                    
                    cells.push({
                        linha: linha,
                        coluna: coluna,
                        navio: navio,
                        estadoId: estadoId
                    })
                }
            }
        }

        apiPost('/save-game', {nickname, cells})
    }

    if (message === 'ok' && coluna != undefined && linha != undefined)
    {
        const id = `cell-${linha}-${coluna.toUpperCase()}`;
        let cell = document.getElementById(id);

        if (navios.includes(id)) {
            cell.classList.add("acerto");
            acertos++;

            if (acertos === navios.length) {
                alert("Você acertou todos os navios.");
            }
        } else {
            cell.classList.add("erro");
        }

        acao = undefined;
    }
}

function connect() {
  ws = new WebSocket(WS_URL);

  ws.addEventListener('open', () => {
    console.log('[ws_client] Conectado em', WS_URL);
    // reset backoff
    reconnectInterval = 1000;
  });

  ws.addEventListener('message', (evt) => {
    try {
      const msg = evt.data;
      // Aqui assumimos que o servidor envia a classe como string simples
      console.log('[ws_client] Classe recebida:', msg);
      handleMessage(msg);

      // Se quiser disparar algo na UI, exponha uma função global ou em window
      // Exemplo: window.onClasseRecebida && window.onClasseRecebida(msg);
    } catch (e) {
      console.error('[ws_client] Erro processando mensagem:', e);
    }
  });

  ws.addEventListener('close', (ev) => {
    console.warn('[ws_client] Desconectado. Tentando reconectar em', reconnectInterval, 'ms');
    setTimeout(connect, reconnectInterval);
    // backoff exponencial até 30s
    reconnectInterval = Math.min(30000, reconnectInterval * 2);
  });

  ws.addEventListener('error', (err) => {
    console.error('[ws_client] Erro WebSocket:', err);
    // Forçar reconexão
    try { ws.close(); } catch (e) {}
  });
}

// Iniciar conexão imediatamente
connect();

let acertos = 0;

function clicarCelula(event) {
    let cell = event.target;

    if (cell.classList.contains("erro") || cell.classList.contains("acerto")) {
        return;
    }

    let id = cell.id;

    if (navios.includes(id)) {
        cell.classList.add("acerto");
        acertos++;

        if (acertos === navios.length) {
            alert("Você acertou todos os navios.");
        }
    } else {
        cell.classList.add("erro");
    }
}

function ativarTabuleiro() {
    for (let linha = 1; linha <= linhas; linha++) {
        for (let coluna of colunas) {
            let id = `cell-${linha}-${coluna}`;
            let cell = document.getElementById(id);
            if (cell) {
                cell.addEventListener("click", clicarCelula);
            }
        }
    }
}


carregarMapa();
ativarTabuleiro();