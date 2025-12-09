// Cliente WebSocket para receber classes enviadas pelo servidor Python
// Conecta em ws://localhost:8765 e faz console.log das mensagens recebidas

const WS_URL = 'ws://localhost:8765';
let ws = null;
let reconnectInterval = 1000; // 1s

function connect() {
  ws = new WebSocket(WS_URL);

  ws.addEventListener('open', () => {
    console.log('[ws_client] Conectado em', WS_URL);
    // reset backoff
    reconnectInterval = 1000;
  });

  ws.addEventListener('message', (evt) => {
    try {
      const msg = evt.data;
      // Aqui assumimos que o servidor envia a classe como string simples
      console.log('[ws_client] Classe recebida:', msg);

      // Se quiser disparar algo na UI, exponha uma função global ou em window
      // Exemplo: window.onClasseRecebida && window.onClasseRecebida(msg);
    } catch (e) {
      console.error('[ws_client] Erro processando mensagem:', e);
    }
  });

  ws.addEventListener('close', (ev) => {
    console.warn('[ws_client] Desconectado. Tentando reconectar em', reconnectInterval, 'ms');
    setTimeout(connect, reconnectInterval);
    // backoff exponencial até 30s
    reconnectInterval = Math.min(30000, reconnectInterval * 2);
  });

  ws.addEventListener('error', (err) => {
    console.error('[ws_client] Erro WebSocket:', err);
    // Forçar reconexão
    try { ws.close(); } catch (e) {}
  });
}

// Iniciar conexão imediatamente
connect();
