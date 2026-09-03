#!/usr/bin/env python3
"""
Verifica se todo o sistema está configurado corretamente
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import config

print(" VERIFICANDO SISTEMA...")
print("=" * 50)

# Verificar arquivos necessários
arquivos_necessarios = [
    'src/core/__init__.py',
    'src/core/coletor_dados.py',
    'src/core/classificador.py',
    'src/services/reconhecedor.py',
    'src/core/detector_maos.py',
    'config.py',
    'src/apps/reconhecimento_app.py'
]

print(" Verificando arquivos...")
for arquivo in arquivos_necessarios:
    caminho_arquivo = os.path.join(BASE_DIR, arquivo)
    if os.path.exists(caminho_arquivo):
        print(f" {arquivo}")
    else:
        print(f" {arquivo} - FALTANDO!")

# Verificar se o modelo existe
print("\n Verificando modelo treinado...")
if os.path.exists(os.path.join(config.CONFIG['caminho_modelos'], 'modelo_libras.pkl')):
    print(" Modelo treinado encontrado!")
    print(" Pode executar: python src/apps/reconhecimento_app.py")
else:
    print(" Modelo não encontrado.")
    print(" Execute primeiro: python src/apps/treinamento_app.py")

# Verificar dependências
print("\n Verificando dependências...")
try:
    import cv2
    print(" OpenCV instalado")
except ImportError:
    print(" OpenCV não instalado")

try:
    import mediapipe
    print(" MediaPipe instalado")
except ImportError:
    print(" MediaPipe não instalado")

try:
    import sklearn
    print(" Scikit-learn instalado")
except ImportError:
    print(" Scikit-learn não instalado")

print("\n" + "=" * 50)
print(" Verificação concluída!")