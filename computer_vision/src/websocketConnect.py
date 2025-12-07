import asyncio
import websockets

connected_clients = set()  # Armazena todos os clientes conectados

async def handle_client(websocket, path):
    # Adiciona o cliente à lista de conectados
    connected_clients.add(websocket)
    print("Cliente conectado!")
    try:
        async for message in websocket:
            print(f"Mensagem recebida: {message}")
            await websocket.send(f"Você disse: {message}")
    except websockets.ConnectionClosed:
        print("Cliente desconectou.")
    finally:
        # Remove o cliente quando desconectar
        connected_clients.remove(websocket)

# Função para enviar mensagem a todos os clientes conectados
async def send_message_to_clients(message):
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])
    else:
        print("Nenhum cliente conectado para enviar mensagem.")

# Inicializa o servidor
async def main():
    server = await websockets.serve(handle_client, "localhost", 8765)
    print("Servidor WebSocket rodando em ws://localhost:8765")
    await server.wait_closed()

asyncio.run(main())
