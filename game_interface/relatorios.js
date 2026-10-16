const CHAVE_RESULTADOS = "librasNaval.resultados";

const elementos = {
    totalPartidas: document.getElementById("total-partidas"),
    precisaoMedia: document.getElementById("precisao-media"),
    tempoMedio: document.getElementById("tempo-medio"),
    jogadasLibras: document.getElementById("jogadas-libras"),
    tabelaFaixas: document.getElementById("relatorio-faixas"),
    estadoVazio: document.getElementById("estado-vazio"),
    atualizadoEm: document.getElementById("atualizado-em"),
    exportarCsv: document.getElementById("exportar-csv"),
    exportarJson: document.getElementById("exportar-json"),
    limparRegistros: document.getElementById("limpar-registros"),
};

function carregarResultados() {
    try {
        const resultados = JSON.parse(localStorage.getItem(CHAVE_RESULTADOS) ?? "[]");
        if (!Array.isArray(resultados)) {
            throw new TypeError("O histórico de resultados não é uma lista.");
        }
        return resultados;
    } catch (erro) {
        console.error("Não foi possível ler o histórico de resultados.", erro);
        elementos.estadoVazio.hidden = false;
        elementos.estadoVazio.textContent =
            "Não foi possível ler o histórico salvo neste navegador.";
        return [];
    }
}

function formatarTempo(segundos) {
    const minutos = Math.floor(segundos / 60);
    const segundosRestantes = segundos % 60;
    return minutos ? `${minutos} min ${segundosRestantes} s` : `${segundosRestantes} s`;
}

function formatarPorcentagem(valor) {
    return `${(valor * 100).toFixed(1)}%`;
}

function agruparPorFaixa(resultados) {
    return resultados.reduce((grupos, resultado) => {
        const faixa = resultado.faixaEtariaDescricao ?? "Não informada";
        const grupo = grupos.get(faixa) ?? {
            faixa,
            partidas: 0,
            precisaoTotal: 0,
            duracaoTotal: 0,
            jogadasLibras: 0,
            jogadasMouse: 0,
        };
        grupo.partidas++;
        grupo.precisaoTotal += Number(resultado.precisao) || 0;
        grupo.duracaoTotal += Number(resultado.duracaoSegundos) || 0;
        grupo.jogadasLibras += Number(resultado.jogadasPorLibras) || 0;
        grupo.jogadasMouse += Number(resultado.jogadasPorMouse) || 0;
        grupos.set(faixa, grupo);
        return grupos;
    }, new Map());
}

function criarCelula(texto) {
    const celula = document.createElement("td");
    celula.textContent = texto;
    return celula;
}

function renderizarRelatorio(resultados) {
    const totalPartidas = resultados.length;
    const precisaoTotal = resultados.reduce(
        (total, resultado) => total + (Number(resultado.precisao) || 0),
        0,
    );
    const duracaoTotal = resultados.reduce(
        (total, resultado) => total + (Number(resultado.duracaoSegundos) || 0),
        0,
    );
    const jogadasLibras = resultados.reduce(
        (total, resultado) => total + (Number(resultado.jogadasPorLibras) || 0),
        0,
    );

    elementos.totalPartidas.textContent = totalPartidas;
    elementos.precisaoMedia.textContent = totalPartidas
        ? formatarPorcentagem(precisaoTotal / totalPartidas)
        : "0%";
    elementos.tempoMedio.textContent = totalPartidas
        ? formatarTempo(Math.round(duracaoTotal / totalPartidas))
        : "0 s";
    elementos.jogadasLibras.textContent = jogadasLibras;
    elementos.estadoVazio.hidden = totalPartidas > 0;
    elementos.atualizadoEm.textContent = totalPartidas
        ? `${totalPartidas} partida(s) registrada(s) neste navegador.`
        : "Nenhuma partida registrada.";

    elementos.tabelaFaixas.replaceChildren();
    for (const grupo of agruparPorFaixa(resultados).values()) {
        const linha = document.createElement("tr");
        linha.append(
            criarCelula(grupo.faixa),
            criarCelula(grupo.partidas),
            criarCelula(formatarPorcentagem(grupo.precisaoTotal / grupo.partidas)),
            criarCelula(formatarTempo(Math.round(grupo.duracaoTotal / grupo.partidas))),
            criarCelula(grupo.jogadasLibras),
            criarCelula(grupo.jogadasMouse),
        );
        elementos.tabelaFaixas.append(linha);
    }
}

function escaparCsv(valor) {
    return `"${String(valor ?? "").replaceAll('"', '""')}"`;
}

function baixarArquivo(nome, conteudo, tipo) {
    const arquivo = new Blob([conteudo], { type: tipo });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(arquivo);
    link.download = nome;
    link.click();
    URL.revokeObjectURL(link.href);
}

function exportarCsv(resultados) {
    const colunas = [
        "idSessao",
        "concluidaEm",
        "faixaEtaria",
        "faixaEtariaDescricao",
        "duracaoSegundos",
        "jogadas",
        "acertos",
        "erros",
        "precisao",
        "jogadasPorLibras",
        "jogadasPorMouse",
        "vitoriaCompleta",
    ];
    const linhas = [
        colunas.join(","),
        ...resultados.map((resultado) =>
            colunas.map((coluna) => escaparCsv(resultado[coluna])).join(","),
        ),
    ];
    baixarArquivo("relatorio-librasnaval.csv", linhas.join("\n"), "text/csv;charset=utf-8");
}

function exportarJson(resultados) {
    baixarArquivo(
        "relatorio-librasnaval.json",
        JSON.stringify(resultados, null, 2),
        "application/json",
    );
}

function atualizarPagina() {
    const resultados = carregarResultados();
    renderizarRelatorio(resultados);
    elementos.exportarCsv.onclick = () => exportarCsv(resultados);
    elementos.exportarJson.onclick = () => exportarJson(resultados);
}

elementos.limparRegistros.addEventListener("click", () => {
    const confirmar = window.confirm(
        "Isso apagará todos os registros de partidas deste navegador. " +
        "Os modelos e dados de treinamento não serão alterados. Continuar?",
    );
    if (!confirmar) {
        return;
    }

    localStorage.removeItem(CHAVE_RESULTADOS);
    atualizarPagina();
});

atualizarPagina();
