import cv2
from collections import deque

import config
from src.core.detector_maos import DetectorMaos
from src.core.classificador_temporal import ClassificadorTemporal


class ReconhecimentoDinamico:
    """Reconhece sinais com movimento usando uma janela deslizante."""

    def __init__(self, camera=0, tamanho_janela=45):
        self.camera = int(camera)
        self.tamanho_janela = int(tamanho_janela)
        self.detector = DetectorMaos()
        self.classificador = ClassificadorTemporal()

    def executar(self):
        if not self.classificador.carregar():
            print("Modelo dinâmico não encontrado. Treine ao menos dois sinais.")
            return False

        camera = cv2.VideoCapture(self.camera)
        if not camera.isOpened():
            camera.release()
            print(f"Não foi possível abrir a câmera {self.camera}.")
            return False

        buffer = deque(maxlen=self.tamanho_janela)
        previsao, confianca = "?", 0.0
        try:
            while True:
                sucesso, quadro = camera.read()
                if not sucesso:
                    break
                quadro = cv2.flip(quadro, 1)
                resultado = self.detector.maos.process(
                    cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)
                )
                if resultado.multi_hand_landmarks:
                    marcos = resultado.multi_hand_landmarks[0]
                    self.detector.desenhar_landmarks(quadro, marcos)
                    buffer.append(self.detector.extrair_caracteristicas(marcos))
                    if len(buffer) == self.tamanho_janela:
                        previsao, confianca = self.classificador.prever(list(buffer))
                cv2.putText(quadro, f"Dinamico: {previsao} ({confianca:.1%})",
                            (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (0, 255, 0), 2)
                cv2.putText(quadro, "Q encerra", (15, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.imshow("Reconhecimento dinamico", quadro)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            camera.release()
            cv2.destroyAllWindows()
        return True
