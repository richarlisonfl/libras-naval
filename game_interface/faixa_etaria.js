const faixaElement = document.getElementById('faixa-selecionada');
const botaoConfirmar = document.getElementById('btn-confirmar');
const faixas = {
    '1': 'Até 6 anos',
    '2': '7 a 10 anos',
    '3': '11 a 14 anos',
    '4': '15 a 17 anos',
    '5': '18 anos ou mais'
};

let faixaSelecionada = null;
const worker = new SharedWorker('ws-sw.js');
worker.port.start();

worker.port.onmessage = (evento) => {
    if (evento.data.tipo !== 'message') {
        return;
    }

    const mensagem = evento.data.mensagem.toString().toLowerCase().trim();
    if (Object.prototype.hasOwnProperty.call(faixas, mensagem)) {
        selecionarFaixa(mensagem);
    } else if (mensagem === 'ok' && faixaSelecionada) {
        void confirmarFaixa();
    } else if (mensagem === 'limpar') {
        limparSelecao();
    } else if (mensagem === 'iniciar' && faixaSelecionada) {
        void confirmarFaixa();
    }
};

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-faixa]').forEach((elemento) => {
        elemento.addEventListener('click', () => selecionarFaixa(elemento.dataset.faixa));
    });
    botaoConfirmar.addEventListener('click', () => void confirmarFaixa());
});

function selecionarFaixa(numero) {
    faixaSelecionada = numero;
    document.querySelectorAll('[data-faixa]').forEach((elemento) => {
        elemento.classList.toggle('selecionado', elemento.dataset.faixa === numero);
    });
    faixaElement.textContent = `${numero} - ${faixas[numero]}`;
    botaoConfirmar.disabled = false;
}

function limparSelecao() {
    faixaSelecionada = null;
    document.querySelectorAll('[data-faixa]').forEach((elemento) => {
        elemento.classList.remove('selecionado');
    });
    faixaElement.textContent = 'Aguardando seleção...';
    botaoConfirmar.disabled = true;
}

async function confirmarFaixa() {
    if (!faixaSelecionada) {
        return;
    }
    const idSessao = crypto.randomUUID();
    localStorage.setItem('faixa_etaria', faixaSelecionada);
    localStorage.setItem('id_sessao', idSessao);
    botaoConfirmar.disabled = true;
    botaoConfirmar.textContent = 'Iniciando jogo...';
    setTimeout(() => {
        window.location.href = 'game.html';
    }, 800);
}
