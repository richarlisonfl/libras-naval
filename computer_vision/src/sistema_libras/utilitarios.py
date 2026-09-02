import mediapipe as mp
import numpy as np


class UtilitariosMaos:
    ANGULOS_PONTOS = (
        (5, 6, 8),
        (9, 10, 12),
        (13, 14, 16),
        (17, 18, 20),
    )

    def __init__(self):
        self.mp_maos = mp.solutions.hands
        self.mp_desenho = mp.solutions.drawing_utils
        self.maos = self.mp_maos.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )

    def extrair_caracteristicas(self, marcos_mao):
        """Extrai coordenadas dos pontos e ângulos da mão."""
        caracteristicas = []

        for marco in marcos_mao.landmark:
            caracteristicas.extend((marco.x, marco.y, marco.z))

        caracteristicas.extend(self._calcular_angulos(marcos_mao))
        return np.array(caracteristicas, dtype=float)

    def _calcular_angulos(self, marcos_mao):
        """Calcula os ângulos definidos entre os pontos dos dedos."""
        pontos = marcos_mao.landmark
        angulos = []

        for indice_inicio, indice_meio, indice_fim in self.ANGULOS_PONTOS:
            vetor_inicio = np.array([
                pontos[indice_inicio].x - pontos[indice_meio].x,
                pontos[indice_inicio].y - pontos[indice_meio].y,
            ])
            vetor_fim = np.array([
                pontos[indice_fim].x - pontos[indice_meio].x,
                pontos[indice_fim].y - pontos[indice_meio].y,
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
        self.mp_desenho.draw_landmarks(
            imagem,
            marcos_mao,
            self.mp_maos.HAND_CONNECTIONS,
            self.mp_desenho.DrawingSpec(
                color=(0, 255, 0),
                thickness=2,
                circle_radius=2,
            ),
            self.mp_desenho.DrawingSpec(
                color=(255, 0, 0),
                thickness=2,
            ),
        )