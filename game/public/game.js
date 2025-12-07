const linhas = 5;
const colunas = ["A", "E", "I", "O", "U"];

let navios = [];
let acertos = 0;

async function carregarMapa() {
    try {
        let resposta = await fetch("mapa.json");
        let dados = await resposta.json();
        navios = dados.navios;
        ativarTabuleiro();
    } catch (erro) {
        alert("Erro ao carregar o mapa.");
    }
}

carregarMapa();

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
