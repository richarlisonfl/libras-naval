import { apiGet, apiPost } from "./api.js";

// Elementos DOM
const gradeNomes = document.getElementById('grade-nomes');
const nomeSelecionadoElement = document.getElementById('nome-selecionado');
const btnConfirmar = document.getElementById('btn-confirmar');

// Variáveis de estado
let nomeSelecionado = '';
let mapeamentoNomes = {};

let coluna = undefined;
let linha = undefined;

const worker = new SharedWorker("ws-sw.js");
worker.port.start();

worker.port.onmessage = (ev) => {
    if (ev.data.tipo !== 'message')
        return;

    const mensagem = ev.data.mensagem.toString().toLowerCase().trim(); 
    
    // Vogais para colunas
    if (['a', 'e', 'i', 'o', 'u'].includes(mensagem)) {
        coluna = mensagem.toUpperCase();
        console.log(`Coluna selecionada: ${coluna}`);
        
        // Feedback visual (opcional)
        highlightColuna(coluna);
    }
    
    // Números para linhas
    else if (['1', '2', '3', '4', '5'].includes(mensagem)) {
        linha = mensagem;
        console.log(`Linha selecionada: ${linha}`);
        
        // Feedback visual (opcional)
        highlightLinha(linha);
    }
    
    // OK para confirmar seleção
    else if (mensagem === 'ok' && coluna && linha) {
        const coordenada = `${coluna}${linha}`;
        const nome = mapeamentoNomes[coordenada];
        
        if (nome) {
            selecionarNome(coordenada, nome);
        }
        
        // Limpar highlights
        clearHighlights();
        
        // Limpar seleção
        coluna = undefined;
        linha = undefined;
    }
    
    // Limpar seleção
    else if (mensagem === 'limpar') {
        coluna = undefined;
        linha = undefined;
        console.log('Seleção limpa');
        clearHighlights();
    }
    
    // Navegação para o jogo (sinal "ily")
    else if (mensagem === 'iniciar') {
        if (nomeSelecionado) {
            confirmarEscolha();
        } else {
            console.log('⚠️  Selecione um nome primeiro');
        }
    }
};

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando escolha de nome...');
    
    // Carregar nomes do JSON
    carregarNomes();
    
    // Configurar evento do botão
    btnConfirmar.addEventListener('click', confirmarEscolha);
});

async function carregarNomes() {
    try {
        const result = await apiGet('/get-nickname');
        const nicknames = result.nicknames;
        let nicknameIndex = 0;
        for (let linha = 1; linha < 6; linha++) {
            for (let coluna of ['A', 'E', 'I', 'O', 'U'])
            {
                mapeamentoNomes[`${coluna}${linha}`] = nicknames[nicknameIndex].apelido;
                
                if (nicknames.length == nicknameIndex)
                    break;

                nicknameIndex++
            }
        }
        renderizarGrade();
    } catch (erro) {
        console.error('Erro ao carregar nomes:', erro);
        
        // Fallback para nomes padrão
        mapeamentoNomes = {
            'A1': 'Miguel', 'E1': 'Arthur', 'I1': 'Gael', 'O1': 'Heitor', 'U1': 'Theo',
            'A2': 'Davi', 'E2': 'Gabriel', 'I2': 'Bernardo', 'O2': 'Samuel', 'U2': 'João',
            'A3': 'Lorenzo', 'E3': 'Benjamin', 'I3': 'Pedro', 'O3': 'Matheus', 'U3': 'Lucas',
            'A4': 'Alice', 'E4': 'Sophia', 'I4': 'Helena', 'O4': 'Valentina', 'U4': 'Laura',
            'A5': 'Isabella', 'E5': 'Manuela', 'I5': 'Júlia', 'O5': 'Heloísa', 'U5': 'Luiza'
        };
        
        renderizarGrade();
    }
}

// Renderizar grade 5x5
function renderizarGrade() {
    gradeNomes.innerHTML = '';
    
    // Coordenadas possíveis
    const linhas = [1, 2, 3, 4, 5];
    const colunas = ['A', 'E', 'I', 'O', 'U'];
    
    // Criar grade 5x5 na ordem correta (A1, E1, I1, O1, U1, A2, E2...)
    linhas.forEach(linha => {
        colunas.forEach(coluna => {
            const coordenada = `${coluna}${linha}`;
            const nome = mapeamentoNomes[coordenada] || 'Nome';
            
            const celula = document.createElement('div');
            celula.className = 'celula-nome';
            celula.dataset.coordenada = coordenada;
            celula.textContent = nome;
            
            // Tooltip para mostrar coordenada
            celula.title = `Coordenada: ${coordenada}`;
            
            celula.addEventListener('click', () => selecionarNome(coordenada, nome));
            
            gradeNomes.appendChild(celula);
        });
    });
}

// Selecionar nome (clique manual)
function selecionarNome(coordenada, nome) {
    console.log(`Nome selecionado: ${nome} (${coordenada})`);
    
    nomeSelecionado = nome;
    
    // Remover seleção anterior
    document.querySelectorAll('.celula-nome').forEach(celula => {
        celula.classList.remove('selecionado');
    });
    
    // Marcar como selecionado
    const celulaSelecionada = document.querySelector(`[data-coordenada="${coordenada}"]`);
    if (celulaSelecionada) {
        celulaSelecionada.classList.add('selecionado');
    }
    
    // Atualizar display
    nomeSelecionadoElement.textContent = `${nome} (${coordenada})`;
    nomeSelecionadoElement.style.color = '#202124';
    
    // Habilitar botão
    btnConfirmar.disabled = false;
}

// Funções de feedback visual para coordenadas
function highlightColuna(letra) {
    // Remove highlight anterior
    document.querySelectorAll('.letra-coluna').forEach(el => {
        el.style.backgroundColor = '#81c995';
    });
    
    // Destaca a coluna selecionada
    const colunas = document.querySelectorAll('.letra-coluna');
    const indices = { 'A': 0, 'E': 1, 'I': 2, 'O': 3, 'U': 4 };
    if (indices[letra] !== undefined && colunas[indices[letra]]) {
        colunas[indices[letra]].style.backgroundColor = '#ffe28a';
    }
}

function highlightLinha(numero) {
    // Remove highlight anterior
    document.querySelectorAll('.numero-linha').forEach(el => {
        el.style.backgroundColor = '#81c995';
    });
    
    // Destaca a linha selecionada
    const linhas = document.querySelectorAll('.numero-linha');
    const index = parseInt(numero) - 1;
    if (linhas[index]) {
        linhas[index].style.backgroundColor = '#ffe28a';
    }
}

function clearHighlights() {
    document.querySelectorAll('.letra-coluna, .numero-linha').forEach(el => {
        el.style.backgroundColor = '#81c995';
    });
}

// Confirmar escolha e ir para o jogo
function confirmarEscolha() {
    if (!nomeSelecionado) {
        return;
    }
    
    console.log(`Confirmando nome: ${nomeSelecionado}`);
    console.log('Redirecionando para game.html');
    
    // Salvar no localStorage
    localStorage.setItem('apelido', nomeSelecionado);
    
    // Desabilitar botão para evitar múltiplos cliques
    btnConfirmar.disabled = true;
    btnConfirmar.textContent = 'Iniciando Jogo...';
    
    // Feedback visual
    nomeSelecionadoElement.style.backgroundColor = '#81c995';
    nomeSelecionadoElement.style.color = 'white';
    
    // Redirecionar para game.html
    setTimeout(() => {
        window.location.href = 'game.html';
    }, 800);
}

// Exportar funções para uso global
window.selecionarNome = selecionarNome;
window.confirmarEscolha = confirmarEscolha;