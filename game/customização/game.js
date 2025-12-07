// Configurações básicas
const linhas = 5;
const colunas = ["A", "E", "I", "O", "U"];

// Variáveis do jogo
let navios = [];
let acertos = 0;
let erros = 0;

// Carrega o mapa do arquivo JSON
async function iniciarJogo() {
    try {
        const resposta = await fetch("mapa.json");
        const dados = await resposta.json();
        navios = dados.navios;
        
        // Atualiza a tela com número de navios
        document.getElementById('navios-restantes').textContent = navios.length;
        
        // Ativa as células do tabuleiro
        ativarCelulas();
        
        document.getElementById('mensagem-status').textContent = 
            `Encontre ${navios.length} navios escondidos!`;
            
    } catch (erro) {
        alert("Não foi possível carregar o mapa.");
    }
}

// Ativa o clique nas células
function ativarCelulas() {
    for (let linha = 1; linha <= linhas; linha++) {
        for (let coluna of colunas) {
            const id = `cell-${linha}-${coluna}`;
            const celula = document.getElementById(id);
            
            if (celula) {
                celula.addEventListener("click", function(event) {
                    verificarTiro(event.target);
                });
            }
        }
    }
}

// Verifica se o tiro acertou um navio
function verificarTiro(celula) {
    // Se já foi clicada, não faz nada
    if (celula.classList.contains("erro") || celula.classList.contains("acerto")) {
        return;
    }
    
    const id = celula.id;
    
    if (navios.includes(id)) {
        // Acertou um navio
        celula.classList.add("acerto");
        acertos++;
        
        // Atualiza contadores
        document.getElementById('contador-acertos').textContent = acertos;
        document.getElementById('navios-restantes').textContent = navios.length - acertos;
        
        document.getElementById('mensagem-status').textContent = "Acertou um navio!";
        
        // Verifica vitória
        if (acertos === navios.length) {
            document.getElementById('mensagem-status').textContent = 
                `Parabéns! Você afundou todos os ${navios.length} navios!`;
            setTimeout(() => alert("Você venceu!"), 500);
        }
        
    } else {
        // Errou (água)
        celula.classList.add("erro");
        erros++;
        document.getElementById('contador-erros').textContent = erros;
        document.getElementById('mensagem-status').textContent = "Água! Tente novamente.";
    }
}

// Inicia o jogo
iniciarJogo();