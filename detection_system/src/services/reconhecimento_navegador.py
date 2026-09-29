import json

from src.core.classificador import ClassificadorLibras
from src.services.websocket import WebsocketServer


class ReconhecimentoNavegador:
    """Recebe características dos landmarks e classifica sem abrir câmera local."""

    PORTA = 8766

    def __init__(self):
        self.classificador = ClassificadorLibras()
        self.servidor = WebsocketServer(
            port=self.PORTA,
            message_callback=self.processar_mensagem,
        )

    def carregar_modelo(self):
        carregado = self.classificador.carregar_modelo()
        if not carregado:
            print("Modelo estático não encontrado. Treine antes do reconhecimento web.")
        return carregado

    def processar_mensagem(self, mensagem):
        try:
            dados = json.loads(mensagem)
            if dados.get("tipo") != "landmarks":
                return json.dumps({"tipo": "erro", "mensagem": "tipo inválido"})
            caracteristicas = dados.get("caracteristicas")
            if not isinstance(caracteristicas, list) or len(caracteristicas) != 68:
                return json.dumps({"tipo": "erro", "mensagem": "68 características esperadas"})
            sinal, confianca = self.classificador.prever(caracteristicas)
            return json.dumps({
                "tipo": "previsao",
                "sinal": sinal,
                "confianca": confianca,
            })
        except (TypeError, ValueError, json.JSONDecodeError) as erro:
            return json.dumps({"tipo": "erro", "mensagem": str(erro)})

    def executar(self):
        if not self.carregar_modelo():
            return False
        print(f"Reconhecimento web ativo em ws://localhost:{self.PORTA}")
        print("Abra teste_camera_navegador.html para enviar landmarks.")
        try:
            while True:
                input()
        except (KeyboardInterrupt, EOFError):
            self.servidor.stop()
        return True