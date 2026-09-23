from collections import deque
import time

import cv2
import numpy as np

import config
from src.core.classificador import ClassificadorLibras
from src.core.classificador_temporal import ClassificadorTemporal
from src.core.detector_maos import DetectorMaos
from src.services import websocket


class ReconhecimentoHibrido:
    """Reconhece sinais estáticos e dinâmicos em uma única captura."""

    def __init__(self, camera=0, tamanho_janela=None):
        self.camera = int(camera)
        self.tamanho_janela = int(
            tamanho_janela or config.CONFIG["janela_dinamica"]
        )
        self.detector = DetectorMaos()
        self.estatico = ClassificadorLibras()
        self.dinamico = ClassificadorTemporal()
        self.buffer = deque(maxlen=self.tamanho_janela)
        self.caracteristicas_anteriores = None
        self.ultima_previsao_enviada = None
        self.tempo_ultima_previsao = 0.0
        try:
            self.websocket_server = websocket.WebsocketServer()
        except Exception as erro:
            print(f"WebSocket indisponível: {erro}")
            self.websocket_server = None

    def carregar_modelos(self):
        modelo_estatico = self.estatico.carregar_modelo()
        modelo_dinamico = self.dinamico.carregar()
        if not modelo_estatico:
            print("Modelo estático não encontrado.")
        if not modelo_dinamico:
            print("Modelo dinâmico não encontrado.")
        return modelo_estatico, modelo_dinamico

    @staticmethod
    def _movimento_atual(caracteristicas, anteriores):
        if anteriores is None:
            return 0.0
        pontos_atuais = np.asarray(caracteristicas[:63])
        pontos_anteriores = np.asarray(anteriores[:63])
        return float(np.mean(np.linalg.norm(
            (pontos_atuais - pontos_anteriores).reshape(-1, 3), axis=1
        )))

    def _escolher_previsao(self, previsao_estatica, confianca_estatica,
                           previsao_dinamica, confianca_dinamica, movimento):
        movimento_ativo = movimento >= config.CONFIG["limiar_movimento"]
        dinamico_disponivel = previsao_dinamica != "?"
        if (
            movimento_ativo
            and dinamico_disponivel
            and confianca_dinamica >= config.CONFIG["limite_confianca_dinamico"]
        ):
            return previsao_dinamica, confianca_dinamica, "dinâmico"
        if previsao_estatica != "?":
            return previsao_estatica, confianca_estatica, "estático"
        if dinamico_disponivel:
            return previsao_dinamica, confianca_dinamica, "dinâmico"
        return "?", 0.0, "nenhum"

    def _enviar_previsao(self, previsao, confianca):
        if (
            previsao == "?"
            or confianca <= config.CONFIG["limite_confianca_envio"]
        ):
            return
        agora = time.time()
        mesma_previsao = previsao == self.ultima_previsao_enviada
        passou_intervalo = (
            agora - self.tempo_ultima_previsao
            > config.CONFIG["intervalo_envio_sinal"]
        )
        if mesma_previsao and not passou_intervalo:
            return
        if self.websocket_server is not None:
            self.websocket_server.send_message(previsao)
        self.ultima_previsao_enviada = previsao
        self.tempo_ultima_previsao = agora

    def executar(self):
        modelo_estatico, modelo_dinamico = self.carregar_modelos()
        if not modelo_estatico and not modelo_dinamico:
            print("Treine sinais estáticos ou dinâmicos antes do reconhecimento.")
            return False

        camera = cv2.VideoCapture(self.camera)
        if not camera.isOpened():
            camera.release()
            print(f"Não foi possível abrir a câmera {self.camera}.")
            return False

        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CONFIG["dimensao_imagem"][0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CONFIG["dimensao_imagem"][1])
        camera.set(cv2.CAP_PROP_FPS, config.CONFIG["fps_camera"])
        print("Reconhecimento híbrido iniciado. Pressione 'q' para sair.")

        try:
            while True:
                sucesso, quadro = camera.read()
                if not sucesso:
                    break
                quadro = cv2.flip(quadro, 1)
                resultado = self.detector.maos.process(
                    cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)
                )
                previsao, confianca, origem = "?", 0.0, "nenhum"
                movimento = 0.0

                if resultado.multi_hand_landmarks:
                    marcos = resultado.multi_hand_landmarks[0]
                    self.detector.desenhar_landmarks(quadro, marcos)
                    caracteristicas = self.detector.extrair_caracteristicas(marcos)
                    movimento = self._movimento_atual(
                        caracteristicas, self.caracteristicas_anteriores
                    )
                    self.caracteristicas_anteriores = caracteristicas
                    self.buffer.append(caracteristicas)

                    previsao_estatica, confianca_estatica = "?", 0.0
                    previsao_dinamica, confianca_dinamica = "?", 0.0
                    if modelo_estatico:
                        previsao_estatica, confianca_estatica = self.estatico.prever(
                            caracteristicas
                        )
                    if modelo_dinamico and len(self.buffer) == self.tamanho_janela:
                        previsao_dinamica, confianca_dinamica = self.dinamico.prever(
                            list(self.buffer)
                        )
                    previsao, confianca, origem = self._escolher_previsao(
                        previsao_estatica, confianca_estatica,
                        previsao_dinamica, confianca_dinamica, movimento
                    )
                    self._enviar_previsao(previsao, confianca)
                else:
                    self.caracteristicas_anteriores = None
                    self.buffer.clear()

                cv2.putText(
                    quadro, f"SINAL: {previsao} ({confianca:.1%}) - {origem}",
                    (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
                )
                cv2.putText(
                    quadro, f"MOVIMENTO: {movimento:.4f} | Q encerra",
                    (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2,
                )
                cv2.imshow("Reconhecimento de Libras", quadro)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            camera.release()
            cv2.destroyAllWindows()
        return True