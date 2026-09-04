import cv2
import numpy as np

import config
from src.core.classificador import ClassificadorLibras
from src.core.classificador_temporal import ClassificadorTemporal
from src.core.detector_maos import DetectorMaos


class TreinoSinais:
    """Coleta e treina um sinal por sessão, estático ou dinâmico."""

    def __init__(self, camera=0):
        self.camera = int(camera)
        self.detector = DetectorMaos()

    def executar(self, modo, sinal, amostras, pessoa):
        if modo not in ("estatico", "dinamico"):
            raise ValueError("O modo deve ser estatico ou dinamico.")
        if not sinal.strip():
            raise ValueError("O sinal não pode ficar vazio.")
        if modo == "estatico":
            dados = self._coletar_estatico(sinal, amostras)
            return self._treinar_estatico(
                dados, [sinal] * len(dados), sinal, pessoa
            )
        sequencias = self._coletar_dinamico(sinal, amostras)
        return self._treinar_dinamico(sequencias, sinal, pessoa)

    def _abrir_camera(self):
        camera = cv2.VideoCapture(self.camera)
        if not camera.isOpened():
            camera.release()
            raise RuntimeError(f"Não foi possível abrir a câmera {self.camera}.")
        return camera

    def _coletar_estatico(self, sinal, amostras):
        camera = self._abrir_camera()
        dados = []
        try:
            while len(dados) < amostras:
                sucesso, quadro = camera.read()
                if not sucesso:
                    continue
                quadro = cv2.flip(quadro, 1)
                resultados = self.detector.maos.process(
                    cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)
                )
                for marcos in resultados.multi_hand_landmarks:
                    self.detector.desenhar_landmarks(quadro, marcos)
                cv2.putText(quadro, f"Sinal: {sinal} {len(dados)}/{amostras}",
                            (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (0, 255, 0), 2)
                cv2.putText(quadro, "ESPACO captura | Q encerra",
                            (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 2)
                cv2.imshow("Treino de sinal estatico", quadro)
                tecla = cv2.waitKey(1) & 0xFF
                if tecla == ord("q"):
                    break
                if tecla == ord(" ") and resultados.multi_hand_landmarks:
                    dados.append(self.detector.extrair_caracteristicas(
                        resultados.multi_hand_landmarks[0]
                    ))
        finally:
            camera.release()
            cv2.destroyAllWindows()
        return dados

    def _coletar_dinamico(self, sinal, frames):
        camera = self._abrir_camera()
        sequencia = []
        try:
            while len(sequencia) < frames:
                sucesso, quadro = camera.read()
                if not sucesso:
                    continue
                quadro = cv2.flip(quadro, 1)
                resultados = self.detector.maos.process(
                    cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)
                )
                cv2.putText(quadro, f"Sinal: {sinal} frame {len(sequencia)}/{frames}",
                            (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 0), 2)
                cv2.putText(quadro, "Q encerra",
                            (15, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (255, 255, 255), 2)
                cv2.imshow("Treino de sinal dinamico", quadro)
                tecla = cv2.waitKey(1) & 0xFF
                if tecla == ord("q"):
                    break
                if resultados.multi_hand_landmarks:
                    sequencia.append(self.detector.extrair_caracteristicas(
                        resultados.multi_hand_landmarks[0]
                    ))
        finally:
            camera.release()
            cv2.destroyAllWindows()
        if len(sequencia) < 2:
            raise RuntimeError("O sinal dinâmico precisa de ao menos dois frames.")
        return [sequencia]

    def _treinar_estatico(self, dados_novos, rotulos_novos, sinal, pessoa):
        classificador = ClassificadorLibras()
        salvos = classificador.carregar_dados_treinamento()
        dados, rotulos, grupos = salvos or ([], [], None)
        dados.extend(dados_novos)
        rotulos.extend(rotulos_novos)
        classificador.salvar_dados_treinamento(dados, rotulos, grupos=grupos)
        ClassificadorTemporal().atualizar_catalogo(sinal, "estatico", pessoa)
        if len(set(rotulos)) < 2:
            print("Dados salvos. Treine outro sinal para gerar o modelo estático.")
            return None
        precisao = classificador.treinar(dados, rotulos, grupos=grupos)
        classificador.salvar_modelo()
        return precisao

    def _treinar_dinamico(self, sequencias_novas, sinal, pessoa):
        classificador = ClassificadorTemporal()
        sequencias, rotulos = classificador.carregar_dados()
        sequencias.extend(sequencias_novas)
        rotulos.extend([sinal] * len(sequencias_novas))
        classificador.salvar(sequencias, rotulos)
        classificador.atualizar_catalogo(sinal, "dinamico", pessoa)
        if len(set(rotulos)) < 2:
            print("Sequência salva. Treine outro sinal para gerar o modelo dinâmico.")
            return None
        precisao = classificador.treinar(sequencias, rotulos)
        classificador.salvar(sequencias, rotulos)
        return precisao
