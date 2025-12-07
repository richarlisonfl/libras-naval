#!/usr/bin/env python3
"""
Teste rápido da câmera e MediaPipe
"""

import cv2
import mediapipe as mp

print("🔍 Testando câmera...")

# Testar câmera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Câmera não encontrada!")
    # Tentar outros índices de câmera
    for i in range(5):
        camera = cv2.VideoCapture(i)
        if camera.isOpened():
            print(f"✅ Câmera encontrada no índice {i}")
            break
else:
    print("✅ Câmera principal funcionando!")

# Testar MediaPipe
print("🔍 Testando MediaPipe...")
try:
    mp_maos = mp.solutions.hands
    maos = mp_maos.Hands()
    print("✅ MediaPipe carregado com sucesso!")
    
    # Testar captura rápida
    print("🎥 Testando captura (5 segundos)...")
    
    for i in range(100):  # ~5 segundos
        sucesso, imagem = camera.read()
        if sucesso:
            imagem = cv2.flip(imagem, 1)
            resultados = maos.process(cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB))
            
            if resultados.multi_hand_landmarks:
                print("✅ Mão detectada!")
                break
                
            cv2.imshow("Teste Câmera", imagem)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    else:
        print("⚠️  Nenhuma mão detectada durante o teste")
        
except Exception as e:
    print(f"❌ Erro no MediaPipe: {e}")

camera.release()
cv2.destroyAllWindows()
print("✅ Teste concluído!")