// vlibras-sinais.js - Sistema de tradução de texto para sinais de Libras

class TradutorLibras {
    constructor() {
        this.widget = null;
        this.iniciarVLibras();
    }
    
    iniciarVLibras() {
        if (typeof VLibras !== 'undefined') {
            this.widget = new window.VLibras.Widget('https://vlibras.gov.br/app');
            console.log(' VLibras pronto para traduzir texto em sinais');
            
            // Aguarda inicialização
            setTimeout(() => {
                this.traduzirParaSinais('Sistema LibrasNaval carregado.');
            }, 2000);
        }
    }
    
    // Traduz texto para sinais de Libras
    traduzirParaSinais(texto) {
        if (!this.widget) {
            console.warn('VLibras não disponível');
            return;
        }
        
        console.log(` Traduzindo para sinais: "${texto}"`);
        
        // Método principal do VLibras para tradução
        if (this.widget.translate) {
            this.widget.translate(texto);
        }
    }
}

// Inicializa automaticamente
let tradutorLibras = null;

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        tradutorLibras = new TradutorLibras();
        window.tradutorLibras = tradutorLibras;
    }, 1500);
});

// Funções globais para usar em todas as páginas
window.Libras = {
    mostrarSinal: (texto) => {
        if (window.tradutorLibras) {
            window.tradutorLibras.traduzirParaSinais(texto);
        } else {
            // Se ainda não carregou, agenda para quando carregar
            setTimeout(() => {
                if (window.tradutorLibras) {
                    window.tradutorLibras.traduzirParaSinais(texto);
                }
            }, 500);
        }
    },
    
    mostrarBoasVindas: () => {
        window.Libras.mostrarSinal('Bem-vindo ao LibrasNaval. Jogo de Batalha Naval em Libras.');
    },
    
    mostrarInstrucoesInicio: () => {
        window.Libras.mostrarSinal('Para começar, faça o sinal I Love You para a câmera.');
    },
    
    mostrarAguardandoSinal: () => {
        window.Libras.mostrarSinal('Aguardando sinal I Love You da câmera.');
    },
    
    mostrarRedirecionando: () => {
        window.Libras.mostrarSinal('Redirecionando para escolha de nome.');
    }
};