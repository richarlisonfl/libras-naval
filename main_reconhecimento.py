#!/usr/bin/env python3
import cv2
import sys
import os
import warnings

# Suprimir warnings
warnings.filterwarnings('ignore')

# Adicionar o diretório atual ao path para importar o módulo sistema_libras
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sistema_libras.reconhecedor import ReconhecedorLibras
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("📋 Verifique se todos os arquivos do sistema_libras/ existem")
    sys.exit(1)

def main():
    print("RECONHECIMENTO DE LIBRAS")
    
    try:
        reconhecedor = ReconhecedorLibras()
        
        # Verificar se o modelo existe antes de executar
        modelo_carregado = reconhecedor.carregar_modelo()
        
        if modelo_carregado:
            print("✅ Modelo carregado com sucesso!")
            print("🎯 Iniciando reconhecimento em tempo real...")
            print("📝 Instruções:")
            print("   - Mostre os sinais de Libras para a câmera")
            print("   - O sistema identificará letras e números")
            print("   - Pressione 'q' para sair")
            print("-" * 50)
            
            reconhecedor.executar_reconhecimento()
        else:
            print("❌ ERRO: Modelo não encontrado!")
            print("\n📋 Para resolver:")
            print("1. Execute primeiro o treinamento:")
            print("   python main_treinamento.py")
            print("2. Ou use a versão fácil:")
            print("   python main_treinamento_facil.py")
            print("3. Verifique se o arquivo existe:")
            print("   modelos_treinados/modelo_libras.pkl")
            
    except KeyboardInterrupt:
        print("\n🛑 Programa interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        print("💡 Verifique se a câmera está conectada e funcionando")

if __name__ == "__main__":
    main()