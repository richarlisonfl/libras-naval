#!/usr/bin/env python3
"""
Reconhecimento de LIBRAS em tempo real - versão adaptada com suporte a câmera configurável
"""

import cv2
import sys
import os
import warnings
import traceback
import argparse

# Suprimir TODOS os warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Adicionar o diretório atual ao path para importar o módulo sistema_libras
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def parse_args():
    """Parse de argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Reconhecimento de LIBRAS - versão adaptada')
    parser.add_argument('--camera', type=int, default=0, help='Índice da câmera (padrão: 0)')
    return parser.parse_args()


def main():
    """Função principal"""
    args = parse_args()
    
    print("🎯 RECONHECIMENTO DE LIBRAS")
    print(f"📷 Usando câmera: índice {args.camera}")
    print("-" * 60)
    
    try:
        from sistema_libras.reconhecedor import ReconhecedorLibras
        
        print("📦 Carregando componentes...")
        reconhecedor = ReconhecedorLibras(indice_camera=args.camera)
        
        print("🤖 Carregando modelo treinado...")
        if reconhecedor.carregar_modelo():
            print(f"✅ Modelo carregado - {len(reconhecedor.classificador.decoder_rotulos)} classes")
            print("🎥 Iniciando câmera em 3 segundos...")
            print("💡 Mostre os sinais para testar!")
            
            # Pequena pausa para ler as instruções
            import time
            time.sleep(3)
            
            reconhecedor.executar_reconhecimento()
        else:
            print("❌ Modelo não encontrado!")
            print("👉 Execute: python libras_naval.py (e selecione a opção de treinamento)")
            
    except KeyboardInterrupt:
        print("\n👋 Programa finalizado pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print("\n🔍 Detalhes do erro:")
        traceback.print_exc()


if __name__ == "__main__":
    main()
