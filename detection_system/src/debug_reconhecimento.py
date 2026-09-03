#!/usr/bin/env python3
"""
Debug do reconhecimento
"""

import cv2
import numpy as np

from sistema_libras.utilitarios import UtilitariosMaos

print(" Debug - Testando componente por componente...")

# 1. Testar câmera
print("1. Testando câmera...")
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    print(" Câmera OK")
    cv2.imshow('Teste Câmera', frame)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()
else:
    print(" Câmera falhou")
cap.release()

# 2. Testar MediaPipe
print("2. Testando MediaPipe...")
try:
    utilitarios = UtilitariosMaos()
    resultado = utilitarios.maos.process(np.zeros((64, 64, 3), dtype=np.uint8))
    print(" MediaPipe OK")
except Exception as e:
    print(f" MediaPipe falhou: {e}")

# 3. Testar modelo
print("3. Testando modelo...")
try:
    import pickle
    with open('modelos_treinados/modelo_libras.pkl', 'rb') as f:
        model_data = pickle.load(f)
    print(f" Modelo OK - {len(model_data['decoder'])} classes")
except Exception as e:
    print(f" Modelo falhou: {e}")

print(" Agora execute: python main_reconhecimento_limpo.py")