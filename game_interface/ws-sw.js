let filaMensagens = [];
let ws = new WebSocket("ws://localhost:8765");
let portas = [];

onconnect = function(e) {
    const port = e.ports[0];
    portas.push(port);

    ws.onmessage = (ev) => {
        for (const p of portas) {
            p.postMessage({
                tipo: "message",
                mensagem: ev.data
            });
        }
    };
};