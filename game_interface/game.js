let reconnectInterval = 1000;
let coluna = undefined, linha = undefined, acao = undefined;

// VARIÁVEL GLOBAL para controlar redirecionamento
let jogoFinalizado = false;

const worker = new SharedWorker("ws-sw.js");
worker.port.start();

worker.port.onmessage = async (ev) => {
    await handleMessage(ev.data.mensagem);
};

async function handleMessage(rawMessage) {
    const message = rawMessage.toString().toLowerCase().trim();

    if (jogoFinalizado && message === 'ok') 
    {
        redirecionarParaIndex();
    } else if (jogoFinalizado)
        return; // Não processa mais mensagens se jogo acabou
    
    if (['a', 'e', 'i', 'o', 'u'].some((v) => v === message))
    {
        coluna = message;
        atualizarJogadaAtual(coluna, linha);
        atualizarDestaquesTabuleiro(coluna, linha);
    } else if ([1, 2, 3, 4, 5].some((v) => v == message))
    {
        linha = message;
        atualizarJogadaAtual(coluna, linha);
        atualizarDestaquesTabuleiro(coluna, linha);
    } else if (['ok', 'limpar'].some((v) => v === message))
    {
        acao = message;
    }

    if (message === 'limpar')
    {
        coluna = undefined;
        linha = undefined;
        acao = undefined;
        atualizarJogadaAtual(coluna, linha);
        atualizarDestaquesTabuleiro(coluna, linha);
        return;
    }

    if (message === 'salvar')
    {
        finalizarJogoComVitoria();
    }

    if (message === 'ok' && coluna != undefined && linha != undefined)
    {
        const id = `cell-${linha}-${coluna.toUpperCase()}`;
        let cell = document.getElementById(id);

        if (cell && registrarTiro(cell, "libras")) {
            coluna = undefined;
            linha = undefined;
            atualizarJogadaAtual(coluna, linha);
            atualizarDestaquesTabuleiro(coluna, linha);
        }

        acao = undefined;
    }
}

const linhas = 5;
const colunas = ["A", "E", "I", "O", "U"];

let navios = [];
let acertos = 0;
let jogadas = 0;
let erros = 0;
let jogadasPorLibras = 0;
let jogadasPorMouse = 0;
let resultadoRegistrado = false;

const CHAVE_RESULTADOS = "librasNaval.resultados";

function atualizarJogadaAtual(colunaSelecionada, linhaSelecionada) {
    document.getElementById("div-coluna").textContent = colunaSelecionada
        ? `Coluna: ${colunaSelecionada.toUpperCase()}`
        : "Coluna: ";
    document.getElementById("div-linha").textContent = linhaSelecionada
        ? `Linha: ${linhaSelecionada}`
        : "Linha: ";
}

function atualizarDestaquesTabuleiro(colunaSelecionada, linhaSelecionada) {
    document.querySelectorAll(".tabuleiro th.selecionado").forEach((cabecalho) => {
        cabecalho.classList.remove("selecionado");
    });

    if (colunaSelecionada) {
        document.querySelectorAll(".tabuleiro thead th").forEach((cabecalho) => {
            if (cabecalho.textContent.trim() === colunaSelecionada.toUpperCase()) {
                cabecalho.classList.add("selecionado");
            }
        });
    }

    if (linhaSelecionada) {
        document.querySelectorAll(".tabuleiro tbody th").forEach((cabecalho) => {
            if (cabecalho.textContent.trim() === String(linhaSelecionada)) {
                cabecalho.classList.add("selecionado");
            }
        });
    }
}

function mostrarCoordenadaDoMouse(event) {
    const [, linhaSelecionada, colunaSelecionada] = event.currentTarget.id.split("-");
    atualizarJogadaAtual(colunaSelecionada, linhaSelecionada);
    atualizarDestaquesTabuleiro(colunaSelecionada, linhaSelecionada);
}

function restaurarJogadaPorLibras() {
    atualizarJogadaAtual(coluna, linha);
    atualizarDestaquesTabuleiro(coluna, linha);
}

function clicarCelula(event) {
    if (jogoFinalizado) return;
    
    let cell = event.target;

    registrarTiro(cell, "mouse");
}

function registrarTiro(cell, origem) {
    if (cell.classList.contains("erro") || cell.classList.contains("acerto")) {
        return false;
    }

    jogadas++;
    if (origem === "libras") {
        jogadasPorLibras++;
    } else {
        jogadasPorMouse++;
    }

    if (navios.includes(cell.id)) {
        cell.classList.add("acerto");
        acertos++;
        console.log(`Acerto via ${origem}! ${acertos}/${navios.length} navios`);

        if (acertos === navios.length) {
            finalizarJogoComVitoria();
        }
    } else {
        cell.classList.add("erro");
        erros++;
    }

    atualizarContagemNavios();
    return true;
}

function atualizarContagemNavios() {
    const restantes = navios.length - acertos;
    document.getElementById("div-navios-restantes").textContent =
        `Navios restantes: ${restantes}`;
    document.getElementById("div-navios-total").textContent =
        `Total de navios: ${navios.length}`;
}

function ativarTabuleiro() {
    for (let linha = 1; linha <= linhas; linha++) {
        for (let coluna of colunas) {
            let id = `cell-${linha}-${coluna}`;
            let cell = document.getElementById(id);
            if (cell) {
                cell.addEventListener("click", clicarCelula);
                cell.addEventListener("mouseenter", mostrarCoordenadaDoMouse);
                cell.addEventListener("mouseleave", restaurarJogadaPorLibras);
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
        atualizarContagemNavios();
        ativarTabuleiro();
    } catch (erro) {
        alert("Erro ao carregar o mapa.");
    }
}

// FUNÇÃO PRINCIPAL DE FINALIZAÇÃO
function finalizarJogoComVitoria() {
    if (jogoFinalizado) return; // Evita execução múltipla
    
    jogoFinalizado = true;
    clearInterval(cronometro);
    registrarResultadoPartida();
    console.log(' JOGO FINALIZADO - TODOS NAVIOS AFUNDADOS ');
    
    // Desabilita todos os cliques
    document.querySelectorAll('.tabuleiro td').forEach(cell => {
        cell.style.pointerEvents = 'none';
    });
    
    // Opção 1: Modal de vitória
    criarModalVitoria();
}

function registrarResultadoPartida() {
    if (resultadoRegistrado) {
        return;
    }

    const codigoFaixaEtaria = localStorage.getItem("faixa_etaria");
    const resultado = {
        idSessao: localStorage.getItem("id_sessao"),
        concluidaEm: new Date().toISOString(),
        faixaEtaria: codigoFaixaEtaria,
        faixaEtariaDescricao: faixasEtarias[codigoFaixaEtaria] ?? "Não informada",
        duracaoSegundos: totalSegundos,
        jogadas,
        acertos,
        erros,
        precisao: jogadas ? Number((acertos / jogadas).toFixed(4)) : 0,
        jogadasPorLibras,
        jogadasPorMouse,
        vitoriaCompleta: acertos === navios.length,
    };

    try {
        const resultados = JSON.parse(localStorage.getItem(CHAVE_RESULTADOS) ?? "[]");
        if (!Array.isArray(resultados)) {
            throw new TypeError("O histórico de resultados não é uma lista.");
        }
        resultados.push(resultado);
        localStorage.setItem(CHAVE_RESULTADOS, JSON.stringify(resultados));
        resultadoRegistrado = true;
    } catch (erro) {
        console.error("Não foi possível salvar o resultado da partida.", erro);
    }
}

// MODAL DE VITÓRIA
function criarModalVitoria() {
    console.log('Criando modal de vitória...');
    
    const overlay = document.createElement('div');
    overlay.id = 'modal-vitoria-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        padding: 24px;
        background-color: rgba(23, 59, 92, 0.78);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        font-family: "Trebuchet MS", Arial, sans-serif;
    `;
    
    const modal = document.createElement('div');
    modal.id = 'modal-vitoria';
    modal.style.cssText = `
        background: #ffffff;
        padding: clamp(24px, 5vw, 40px);
        border-radius: 18px;
        text-align: center;
        max-width: 600px;
        width: min(100%, 600px);
        border: 1px solid #c9dce1;
        color: #173b5c;
    `;
    
    modal.innerHTML = `
        <h1 style="font-size: clamp(2.2rem, 8vw, 3.5rem); margin: 0 0 20px; color: #173b5c;">Parabéns!</h1>

        <div style="background-color: #e7f3f7;
                    padding: 20px;
                    border-radius: 12px;
                    margin-bottom: 30px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    color: #173b5c;">
            <p id="pResultado" style="font-size: clamp(1.2rem, 4vw, 1.5rem); margin: 10px 0;">
                 ${acertos} navios atingidos
            </p>
        </div>
        
        <div style="font-size: 1.2rem; margin-top: 30px; color: #173b5c;">
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 12px;">
                <button id="btn-voltar-agora" style="background-color: #173b5c; color: white; border: none; padding: 12px 25px; border-radius: 10px; font: inherit; font-size: 1.1rem; cursor: pointer;">
                    Voltar para o início
                </button>
                <button id="btn-jogar-novamente" style="background-color: #4f9d7a; color: white; border: none; padding: 12px 25px; border-radius: 10px; font: inherit; font-size: 1.1rem; cursor: pointer; font-weight: bold;">
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

}

// FUNÇÃO DE REDIRECIONAMENTO
function redirecionarParaIndex() {
    console.log('Redirecionando para index.html...');
    
    // Redireciona
    window.location.href = "index.html";
}

// Adiciona console.log para debug
console.log('game.js carregado. Aguardando jogo...');

let span = document.getElementById('faixa-etaria-jogador')
const faixasEtarias = {
    '1': 'Até 13 anos',
    '2': '14 a 15 anos',
    '3': '16 a 17 anos',
    '4': '18 a 19 anos',
    '5': '20 anos ou mais'
};
span.innerText = faixasEtarias[localStorage.getItem('faixa_etaria')] ?? 'Não informada'

let totalSegundos = 0;

function formatar(seg) {
    const h = String(Math.floor(seg / 3600)).padStart(2, '0');
    const m = String(Math.floor((seg % 3600) / 60)).padStart(2, '0');
    const s = String(seg % 60).padStart(2, '0');
    return `${h}:${m}:${s}`;
}

const cronometro = setInterval(() => {
    totalSegundos++;
    document.getElementById("div-tempo").textContent = `Tempo: ${formatar(totalSegundos)}`;
}, 1000);

document.getElementById("div-coluna").textContent = "Coluna: "
document.getElementById("div-linha").textContent = "Linha: "
atualizarContagemNavios();

carregarMapa();