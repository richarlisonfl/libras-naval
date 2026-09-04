import os
import urllib.request
from pathlib import Path
from types import SimpleNamespace

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class DetectorMaos:
    MODELO_URL = (
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
        "hand_landmarker/float16/1/hand_landmarker.task"
    )
    CONEXOES_MAO = (
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (9, 10), (10, 11), (11, 12),
        (13, 14), (14, 15), (15, 16),
        (17, 18), (18, 19), (19, 20),
        (5, 9), (9, 13), (13, 17), (0, 17),
    )
    ANGULOS_PONTOS = (
        (5, 6, 8),
        (9, 10, 12),
        (13, 14, 16),
        (17, 18, 20),
    )

    def __init__(self):
        caminho_modelo = self._obter_caminho_modelo()
        self.maos = _ProcessadorMaos(self._criar_landmarker(caminho_modelo))

    @staticmethod
    def _criar_landmarker(caminho_modelo):
        opcoes = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=str(caminho_modelo)),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        return vision.HandLandmarker.create_from_options(opcoes)

    def _obter_caminho_modelo(self):
        caminho_configurado = os.environ.get("MEDIAPIPE_HAND_LANDMARKER_MODEL")
        caminho_modelo = Path(caminho_configurado) if caminho_configurado else (
            Path(__file__).resolve().parents[2] / "models" / "hand_landmarker.task"
        )
        if caminho_modelo.exists():
            return caminho_modelo

        caminho_modelo.parent.mkdir(parents=True, exist_ok=True)
        caminho_temporario = caminho_modelo.with_suffix(".task.part")
        try:
            urllib.request.urlretrieve(self.MODELO_URL, caminho_temporario)
            caminho_temporario.replace(caminho_modelo)
        except Exception as erro:
            caminho_temporario.unlink(missing_ok=True)
            raise RuntimeError(
                "Não foi possível obter o modelo hand_landmarker.task. "
                "Defina MEDIAPIPE_HAND_LANDMARKER_MODEL com o caminho do modelo."
            ) from erro
        return caminho_modelo

    def extrair_caracteristicas(self, marcos_mao):
        """Extrai coordenadas dos pontos e ângulos da mão."""
        caracteristicas = []

        for ponto in marcos_mao.landmark:
            caracteristicas.extend((ponto.x, ponto.y, ponto.z))

        caracteristicas.extend(self._calcular_angulos(marcos_mao))
        _, orientacao = self._componente_orientacao(marcos_mao)
        caracteristicas.append(orientacao)
        return np.array(caracteristicas, dtype=float)

    def estimar_orientacao(self, marcos_mao, lado=None):
        """Estima se a palma ou as costas da mão estão voltadas para a câmera."""
        _, componente_camera = self._componente_orientacao(marcos_mao, lado)
        confianca = min(abs(componente_camera), 1.0)
        if confianca < 0.25:
            return "INDEFINIDA", confianca

        orientacao = "PALMA" if componente_camera < 0 else "COSTAS"
        return orientacao, confianca


    def _componente_orientacao(self, marcos_mao, lado=None):
        """Retorna o lado e a componente da normal corrigida para a câmera."""
        pontos = marcos_mao.landmark
        pulso = np.array([pontos[0].x, pontos[0].y, pontos[0].z])
        base_indicador = np.array([pontos[5].x, pontos[5].y, pontos[5].z])
        base_mindinho = np.array([pontos[17].x, pontos[17].y, pontos[17].z])
        vetor_normal = np.cross(base_indicador - pulso, base_mindinho - pulso)
        tamanho_vetor_normal = np.linalg.norm(vetor_normal)
        if tamanho_vetor_normal < 1e-8:
            return "INDEFINIDA", 0.0

        componente = vetor_normal[2] / tamanho_vetor_normal
        lado = lado or getattr(marcos_mao, "lado", None)
        if lado == "Right":
            componente *= -1
        return lado, componente

    def _calcular_angulos(self, marcos_mao):
        """Calcula os ângulos definidos entre os pontos dos dedos."""
        pontos = marcos_mao.landmark
        angulos = []

        for indice_inicio, indice_articulacao, indice_fim in self.ANGULOS_PONTOS:
            vetor_inicio = np.array([
                pontos[indice_inicio].x - pontos[indice_articulacao].x,
                pontos[indice_inicio].y - pontos[indice_articulacao].y,
            ])
            vetor_fim = np.array([
                pontos[indice_fim].x - pontos[indice_articulacao].x,
                pontos[indice_fim].y - pontos[indice_articulacao].y,
            ])

            produto_escalar = np.dot(vetor_inicio, vetor_fim)
            norma_vetores = (
                np.linalg.norm(vetor_inicio) *
                np.linalg.norm(vetor_fim)
            )

            cosseno = produto_escalar / (norma_vetores + 1e-8)
            angulos.append(np.arccos(np.clip(cosseno, -1, 1)))

        return angulos

    def desenhar_landmarks(self, imagem, marcos_mao):
        """Desenha os pontos e conexões da mão na imagem."""
        altura, largura = imagem.shape[:2]
        pontos = [
            (int(ponto.x * largura), int(ponto.y * altura))
            for ponto in marcos_mao.landmark
        ]
        for inicio, fim in self.CONEXOES_MAO:
            cv2.line(imagem, pontos[inicio], pontos[fim], (255, 0, 0), 2)
        for ponto in pontos:
            cv2.circle(imagem, ponto, 2, (0, 255, 0), 2)


class _ProcessadorMaos:
    LADO_FRAME_ESPELHADO_PARA_FISICO = {"Left": "Right", "Right": "Left"}

    def __init__(self, landmarker):
        self._landmarker = landmarker
        self._timestamp_ms = 0

    def process(self, imagem_rgb):
        imagem = mp.Image(image_format=mp.ImageFormat.SRGB, data=imagem_rgb)
        resultado = self._landmarker.detect_for_video(imagem, self._timestamp_ms)
        self._timestamp_ms += 1
        lados = [
            self.LADO_FRAME_ESPELHADO_PARA_FISICO.get(
                classificacao[0].category_name,
                classificacao[0].category_name,
            )
            if classificacao else None
            for classificacao in resultado.handedness
        ]
        landmarks = [
            SimpleNamespace(landmark=pontos_mao, lado=lado)
            for pontos_mao, lado in zip(resultado.hand_landmarks, lados)
        ]
        return SimpleNamespace(
            multi_hand_landmarks=landmarks,
            multi_handedness=[
                [
                    SimpleNamespace(
                        category_name=lado,
                        score=classificacao[0].score,
                    )
                ]
                for lado, classificacao in zip(
                    [landmark.lado for landmark in landmarks], resultado.handedness
                )
            ],
            multi_hand_world_landmarks=[
                SimpleNamespace(landmark=pontos_mao)
                for pontos_mao in resultado.hand_world_landmarks
            ],
        )
