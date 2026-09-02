const worker = new SharedWorker("ws-sw.js");
worker.port.start();

worker.port.onmessage = (ev) => {
    if (ev.data.tipo !== 'message')
        return;

    const mensagem = ev.data.mensagem.toString().toLowerCase().trim(); 
    
    if (mensagem === "iniciar") {
        redirecionarParaEscolhaNome();
    }
};

function atualizarTextoBotao(texto) {
    const botao = document.querySelector('.btn-libras');
    if (botao) {
        botao.textContent = texto;
    }
}

function redirecionarParaEscolhaNome() {
    // Redireciona imediatamente
    window.location.href = 'nome.html';
}

function iniciarModoLibras() {
    console.log('Usando modo manual (clique)');
    redirecionarParaEscolhaNome();
}

localStorage.clear();

// Torna função global para o botão
window.iniciarModoLibras = iniciarModoLibras;