import cv2
import mediapipe as mp
import numpy as np

class UtilitariosMaos:
    def __init__(self):
        self.mp_maos = mp.solutions.hands
        self.maos = self.mp_maos.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_desenho = mp.solutions.drawing_utils
    
    def extrair_caracteristicas(self, marcos_mao):
        """Extrai características normalizadas da mão"""
        caracteristicas = []
        
        # Coordenadas de todos os 21 landmarks
        for marco in marcos_mao.landmark:
            caracteristicas.extend([marco.x, marco.y, marco.z])
        
        # Ângulos entre dedos
        caracteristicas.extend(self._calcular_angulos(marcos_mao))
        
        return np.array(caracteristicas)
    
    def _calcular_angulos(self, marcos_mao):
        """Calcula ângulos entre pontos-chave da mão"""
        angulos = []
        pontos = marcos_mao.landmark
        
        # Ângulo entre dedos (exemplo: entre indicador e médio)
        indices_pontos = [(5,6,8), (9,10,12), (13,14,16), (17,18,20)]  # Base, meio, ponta
        
        for i1, i2, i3 in indices_pontos:
            v1 = np.array([pontos[i1].x - pontos[i2].x, pontos[i1].y - pontos[i2].y])
            v2 = np.array([pontos[i3].x - pontos[i2].x, pontos[i3].y - pontos[i2].y])
            
            cos_angulo = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
            angulo = np.arccos(np.clip(cos_angulo, -1, 1))
            angulos.append(angulo)
        
        return angulos
    
    def desenhar_landmarks(self, imagem, marcos_mao):
        """Desenha landmarks na imagem"""
        self.mp_desenho.draw_landmarks(
            imagem, marcos_mao, self.mp_maos.HAND_CONNECTIONS,
            self.mp_desenho.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            self.mp_desenho.DrawingSpec(color=(255, 0, 0), thickness=2)
        )