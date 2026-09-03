#!/usr/bin/env python3
"""
Verifica se todo o sistema está configurado corretamente
"""

import os
import sys
import config

print(" VERIFICANDO SISTEMA...")
print("=" * 50)

# Verificar arquivos necessários
arquivos_necessarios = [
    'sistema_libras/__init__.py',
    'sistema_libras/coletor_dados.py',
    'sistema_libras/classificador.py',
    'sistema_libras/reconhecedor.py',
    'sistema_libras/utilitarios.py',
    'config.py',
    'main_reconhecimento.py'
]

print(" Verificando arquivos...")
for arquivo in arquivos_necessarios:
    if os.path.exists(arquivo):
        print(f" {arquivo}")
    else:
        print(f" {arquivo} - FALTANDO!")

# Verificar se o modelo existe
print("\n Verificando modelo treinado...")
if os.path.exists(os.path.join(config.CONFIG['caminho_modelos'], 'modelo_libras.pkl')):
    print(" Modelo treinado encontrado!")
    print(" Pode executar: python main_reconhecimento.py")
else:
    print(" Modelo não encontrado.")
    print(" Execute primeiro: python main_treinamento_facil.py")

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