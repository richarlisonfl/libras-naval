import asyncio
import websockets
import threading
import time


class WebsocketServer:
    """Servidor WebSocket simples que roda em um loop próprio (thread).

    - Inicia o servidor no construtor e mantém um event loop dedicado em thread.
    - Exponibiliza `send_message` (thread-safe) para enviar a todos os clientes.
    """

    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port
        self.connected_clients = set()
        self._loop = None
        self._thread = None
        self._server = None
        self._start()

    async def _handler(self, websocket, path=None):
        # Adiciona o cliente à lista de conectados
        self.connected_clients.add(websocket)
        print("Cliente conectado!")
        try:
            async for message in websocket:
                print(f"Mensagem recebida: {message}")
                # ecoa por enquanto
                await websocket.send(f"Você disse: {message}")
        except websockets.ConnectionClosed:
            print("Cliente desconectou.")
        finally:
            self.connected_clients.discard(websocket)

    async def _start_async(self):
        self._server = await websockets.serve(self._handler, self.host, self.port)
        print(f"Servidor WebSocket rodando em ws://{self.host}:{self.port}")

    def _start(self):
        if self._loop is not None:
            return
        self._loop = asyncio.new_event_loop()

        def _run():
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._start_async())
            self._loop.run_forever()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        # breve pausa para o servidor subir
        time.sleep(0.1)

    async def _broadcast(self, message):
        if not self.connected_clients:
            print("Nenhum cliente conectado para enviar mensagem.")
            return
        await asyncio.gather(*(client.send(message) for client in self.connected_clients), return_exceptions=True)

    def send_message(self, message):
        """Envia `message` para todos os clientes conectados de forma thread-safe."""
        if self._loop is None:
            print("Loop do servidor não iniciado.")
            return
        try:
            asyncio.run_coroutine_threadsafe(self._broadcast(message), self._loop)
        except Exception as e:
            print("Erro ao agendar broadcast:", e)

    def stop(self):
        if self._loop is None:
            return
        def _stop_loop():
            self._server.close()
            # aguardar fechamento
            coro = self._server.wait_closed()
            fut = asyncio.run_coroutine_threadsafe(coro, self._loop)
            fut.result(timeout=2)
            self._loop.stop()

        try:
            threading.Thread(target=_stop_loop, daemon=True).start()
        except Exception:
            pass


# Permitir uso rápido: se executado como script, iniciar servidor
if __name__ == '__main__':
    srv = WebsocketServer()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.stop()
