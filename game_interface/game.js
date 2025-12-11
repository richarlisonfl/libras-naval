import { apiGet, apiPost } from "./api.js";

let reconnectInterval = 1000;
let coluna = undefined, linha = undefined, acao = undefined;

// VARIÁVEL GLOBAL para controlar redirecionamento
let jogoFinalizado = false;

const worker = new SharedWorker("ws-sw.js");
worker.port.start();

worker.port.onmessage = async (ev) => {
    await handleMessage(ev.data.mensagem);
};

async function handleMessage(message){
    if (jogoFinalizado && message === 'ok') 
    {
        redirecionarParaIndex();
    } else if (jogoFinalizado)
        return; // Não processa mais mensagens se jogo acabou
    
    if (['a', 'e', 'i', 'o', 'u'].some((v) => v === message))
    {
        coluna = message;
        document.getElementById("div-coluna").textContent = `Coluna: ${message.toUpperCase()}`;
    } else if ([1, 2, 3, 4, 5].some((v) => v == message))
    {
        linha = message;
        document.getElementById("div-linha").textContent = `Linha: ${message}`;
    } else if (['ok', 'limpar'].some((v) => v === message))
    {
        acao = message;
    }

    if (message === 'limpar')
    {
        document.getElementById("div-coluna").textContent = "Coluna: "
        document.getElementById("div-linha").textContent = "Linha: "
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

        await apiPost('/save-game', {time: formatar(totalSegundos), nickname: localStorage.getItem("apelido"), cells})

        finalizarJogoComVitoria();
    }

    if (message === 'ok' && coluna != undefined && linha != undefined)
    {
        const id = `cell-${linha}-${coluna.toUpperCase()}`;
        let cell = document.getElementById(id);

        if (cell && !cell.classList.contains("erro") && !cell.classList.contains("acerto")) {
            if (navios.includes(id)) {
                cell.classList.add("acerto");
                acertos++;
                console.log(`Acerto! ${acertos}/${navios.length} navios`);
                
                if (acertos === navios.length) {
                    finalizarJogoComVitoria();
                }
            } else {
                cell.classList.add("erro");
            }

            document.getElementById("div-coluna").textContent = "Coluna: "
            document.getElementById("div-linha").textContent = "Linha: "
            coluna = undefined;
            linha = undefined;
        }
        
        document.getElementById("div-navios").textContent = "Acertos: " + `${acertos}/${navios.length}`
        acao = undefined;
    }
}

const linhas = 5;
const colunas = ["A", "E", "I", "O", "U"];

let navios = [];
let acertos = 0;

function clicarCelula(event) {
    if (jogoFinalizado) return;
    
    let cell = event.target;

    if (cell.classList.contains("erro") || cell.classList.contains("acerto")) {
        return;
    }

    let id = cell.id;

    if (navios.includes(id)) {
        cell.classList.add("acerto");
        acertos++;
        console.log(`Acerto via clique! ${acertos}/${navios.length} navios`);

        if (acertos === navios.length) {
            finalizarJogoComVitoria();
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

async function carregarMapa() {
    try {
        let resposta = await fetch("mapas.json");
        let dados = await resposta.json();
        
        // Escolhe mapa aleatório
        const indice = Math.floor(Math.random() * dados.mapas.length);
        navios = dados.mapas[indice].navios;
        
        console.log(`Mapa ${dados.mapas[indice].id} carregado`);
        ativarTabuleiro();
    } catch (erro) {
        alert("Erro ao carregar o mapa.");
    }
}

// FUNÇÃO PRINCIPAL DE FINALIZAÇÃO
function finalizarJogoComVitoria() {
    if (jogoFinalizado) return; // Evita execução múltipla
    
    jogoFinalizado = true;
    console.log('🎉🎉🎉 JOGO FINALIZADO - TODOS NAVIOS AFUNDADOS 🎉🎉🎉');
    
    // Desabilita todos os cliques
    document.querySelectorAll('.tabuleiro td').forEach(cell => {
        cell.style.pointerEvents = 'none';
    });
    
    // Opção 1: Modal de vitória
    criarModalVitoria();
}

// MODAL DE VITÓRIA
async function criarModalVitoria() {
    console.log('Criando modal de vitória...');
    
    const overlay = document.createElement('div');
    overlay.id = 'modal-vitoria-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.85);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        font-family: "Google Sans", arial, sans-serif;
    `;
    
    const modal = document.createElement('div');
    modal.id = 'modal-vitoria';
    modal.style.cssText = `
        background: linear-gradient(135deg, #81c995 0%, #8ab4f8 100%);
        padding: 40px;
        border-radius: 25px;
        text-align: center;
        max-width: 600px;
        width: 80%;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
        border: 5px solid #ffe28a;
        color: #202124;
    `;
    
    modal.innerHTML = `
        <h1 style="font-size: 3.5rem; margin: 0 0 20px 0; color: #202124;">Parabéns, ${localStorage.getItem("apelido")}!</h1>

        <div style="background-color: rgba(255, 255, 255, 0.9); 
                    padding: 20px; 
                    border-radius: 15px;
                    margin-bottom: 30px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    max-height: 350px;
                    overflow-y: auto;
                    overflow-x: hidden; ">
            <p id="pPosicao" style="font-size: 1.3rem; margin: 10px 0;">
                🚢 ${acertos} navios atingidos
            </p>
            <p style="font-size: 1.3rem; margin: 10px 0;">
                
            </p>
            <table id="tabelaRank" border="1" style="border-spacing: 15px 5px;border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="padding:10px">Posição</th>
                        <th style="padding:10px">Usuário</th>
                        <th style="padding:10px">Navios atingidos</th>
                        <th style="padding:10px">Tempo de jogo</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </div>
        
        <div style="font-size: 1.2rem; margin-top: 30px; color: #202124;">
            <div style="margin-top: 20px; display: flex; justify-content: center; gap: 15px;">
                <button id="btn-voltar-agora" style="background-color: #202124; color: white; border: none; padding: 12px 25px; border-radius: 10px; font-size: 1.1rem; cursor: pointer;">
                    Voltar para o início
                </button>
                <button id="btn-jogar-novamente" style="background-color: #ffe28a; color: #202124; border: none; padding: 12px 25px; border-radius: 10px; font-size: 1.1rem; cursor: pointer; font-weight: bold;">
                    Jogar Novamente
                </button>
            </div>
        </div>
    `;
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    
    // Botão "Voltar Agora"
    document.getElementById('btn-voltar-agora').addEventListener('click', function() {
        redirecionarParaIndex();
    });
    
    // Botão "Jogar Novamente" (recarrega a página)
    document.getElementById('btn-jogar-novamente').addEventListener('click', function() {
        window.location.reload();
    });

    const result = await apiGet('/get-rank');
    
    const apelido = localStorage.getItem('apelido');
    const index = result.rank.map(e => e.apelido).indexOf(apelido);

    let pPosicao = document.getElementById('pPosicao')
    pPosicao.innerText = `🚢 ${acertos} navio${acertos == 1 ? '' : 's'} atingido${acertos == 1 ? '' : 's'}, ${index + 1}º lugar`;

    const tbody = document.querySelector("#tabelaRank tbody");
    result.rank.forEach((item, index) => {
        const tr = document.createElement('tr');

        const tdPosicao = document.createElement('td');
        tdPosicao.textContent = `${index + 1}º`;

        const tdUsuario = document.createElement('td');
        tdUsuario.textContent = item.apelido;

        const tdNaviosAtingidos = document.createElement('td');
        tdNaviosAtingidos.textContent = item.total_atingido;

        const tdTempo = document.createElement('td');
        tdTempo.textContent = item.tempo;

        tr.appendChild(tdPosicao);
        tr.appendChild(tdUsuario);
        tr.appendChild(tdNaviosAtingidos);
        tr.appendChild(tdTempo);

        tbody.appendChild(tr);
    });

    let span = document.getElementById('apelido-jogador')
}

// FUNÇÃO DE REDIRECIONAMENTO
function redirecionarParaIndex() {
    console.log('Redirecionando para index.html...');
    
    // Redireciona
    window.location.href = "index.html";
}

// Adiciona console.log para debug
console.log('game.js carregado. Aguardando jogo...');

let span = document.getElementById('apelido-jogador')
span.innerText = localStorage.getItem('apelido') ?? 'super'

let totalSegundos = 0;

function formatar(seg) {
    const h = String(Math.floor(seg / 3600)).padStart(2, '0');
    const m = String(Math.floor((seg % 3600) / 60)).padStart(2, '0');
    const s = String(seg % 60).padStart(2, '0');
    return `${h}:${m}:${s}`;
}

setInterval(() => {
    totalSegundos++;
    document.getElementById("div-tempo").textContent = `Tempo: ${formatar(totalSegundos)}`;
}, 1000);

document.getElementById("div-coluna").textContent = "Coluna: "
document.getElementById("div-linha").textContent = "Linha: "
document.getElementById("div-navios").textContent = "Acertos: " + `${acertos}/${navios.length}`

carregarMapa();