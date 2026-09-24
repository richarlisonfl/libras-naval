let portas = [];
let ws = null;
let reconectarEm = 1000;

function conectar() {
    ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => {
        reconectarEm = 1000;
        console.log("WebSocket do reconhecimento conectado.");
    };

    ws.onmessage = (ev) => {
        for (const port of portas) {
            port.postMessage({
                tipo: "message",
                mensagem: ev.data
            });
        }
    };

    ws.onerror = () => {
        ws.close();
    };

    ws.onclose = () => {
        console.warn(
            `WebSocket desconectado. Nova tentativa em ${reconectarEm} ms.`
        );
        setTimeout(conectar, reconectarEm);
        reconectarEm = Math.min(reconectarEm * 2, 5000);
    };
}

onconnect = function(e) {
    const port = e.ports[0];
    portas.push(port);
};

conectar();