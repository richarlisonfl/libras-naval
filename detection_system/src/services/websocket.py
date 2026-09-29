import asyncio
import websockets
import threading
import time


class WebsocketServer:
    """Servidor WebSocket simples que roda em um loop próprio (thread).

    - Inicia o servidor no construtor e mantém um event loop dedicado em thread.
    - Exponibiliza `send_message` (thread-safe) para enviar a todos os clientes.
    """

    def __init__(self, host='localhost', port=8765, message_callback=None):
        self.host = host
        self.port = port
        self.connected_clients = set()
        self._loop = None
        self._thread = None
        self._server = None
        self.message_callback = message_callback
        self._start()

    async def _handler(self, websocket, path=None):
        # Adiciona o cliente à lista de conectados
        self.connected_clients.add(websocket)
        print("Cliente conectado!")
        try:
            async for message in websocket:
                print(f"Mensagem recebida: {message}")
                if self.message_callback is not None:
                    resposta = self.message_callback(message)
                    if resposta is not None:
                        await websocket.send(resposta)
                else:
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
            print(f"WebSocket: nenhum cliente conectado; mensagem descartada: {message}")
            return False
        clientes = tuple(self.connected_clients)
        print(f"WebSocket: enviando '{message}' para {len(clientes)} cliente(s).")
        resultados = await asyncio.gather(
            *(client.send(message) for client in clientes),
            return_exceptions=True,
        )
        return not any(isinstance(resultado, Exception) for resultado in resultados)

    def send_message(self, message):
        """Envia `message` para todos os clientes conectados de forma thread-safe."""
        if self._loop is None:
            print("Loop do servidor não iniciado.")
            return
        try:
            futuro = asyncio.run_coroutine_threadsafe(
                self._broadcast(message), self._loop
            )
            futuro.add_done_callback(self._registrar_resultado_envio)
        except Exception as e:
            print("Erro ao agendar broadcast:", e)

    @staticmethod
    def _registrar_resultado_envio(futuro):
        try:
            if not futuro.result():
                print("WebSocket: envio não realizado.")
        except Exception as erro:
            print(f"WebSocket: erro no envio: {erro}")

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
