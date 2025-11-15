#!/usr/bin/env python3
import cv2
import sys
import os
import warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suprir logs do TensorFlow
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
def main():
    print("=== SISTEMA DE RECONHECIMENTO DE LIBRAS ===")
    try:
        from sistema_libras.reconhecedor import ReconhecedorLibras
        reconhecedor = ReconhecedorLibras() 
        if reconhecedor.carregar_modelo():
            print("✅ Tudo certo! Iniciando câmera...")
            reconhecedor.executar_reconhecimento()
        else:
            print("❌ Modelo não encontrado. Treine primeiro!")       
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()