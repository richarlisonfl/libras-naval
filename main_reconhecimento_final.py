#!/usr/bin/env python3
import cv2
import sys
import os
import warnings
import traceback

# Suprimir TODOS os warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Adicionar o diretório atual ao path para importar o módulo sistema_libras
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    print("RECONHECIMENTO DE LIBRAS")
    
    try:
        from sistema_libras.reconhecedor import ReconhecedorLibras
        
        print("📦 Carregando componentes...")
        reconhecedor = ReconhecedorLibras()
        
        print("🤖 Carregando modelo treinado...")
        if reconhecedor.carregar_modelo():
            print(f"✅ Modelo carregado - {len(reconhecedor.classificador.decoder_rotulos)} classes")
            print("🎥 Iniciando câmera em 3 segundos...")
            print("💡 Mostre os sinais A, E, I, O, U para testar!")
            
            # Pequena pausa para ler as instruções
            import time
            time.sleep(3)
            
            reconhecedor.executar_reconhecimento()
        else:
            print("❌ Modelo não encontrado!")
            print("👉 Execute: python main_treinamento_facil.py")
            
    except KeyboardInterrupt:
        print("\n👋 Programa finalizado pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        print("\n🔍 Detalhes do erro:")
        traceback.print_exc()

if __name__ == "__main__":
    main()