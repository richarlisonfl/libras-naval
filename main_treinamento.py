#!/usr/bin/env python3
"""
Script principal para treinamento do sistema de Libras
"""

import sys
import os

# Esconde os logs de erro no terminal
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sistema_libras.coletor_dados import ColetorDadosLibras
from sistema_libras.classificador import ClassificadorLibras
import config

def main():
    # Usar apenas as classes definidas em config.py
    todas_classes = config.CONFIG['letras_treinamento'] + config.CONFIG['numeros_treinamento']

    print("=== SISTEMA DE TREINAMENTO PARA LIBRAS ===")
    print("📊 Este script irá coletar dados e treinar o modelo")
    print("📷 Certifique-se de que a câmera está conectada")
    print("-" * 50)
    
    try:
        # 1. Coletar dados
        coletor = ColetorDadosLibras()
        
        print("1. 🎥 Fase de coleta de dados")
        
        print(f"📋 Classes para treinar: {todas_classes}")
        print(f"📈 Amostras por classe: {config.CONFIG['numero_amostras_por_classe']}")
        print("\n💡 Durante a coleta:")
        print("   - ESPAÇO: capturar amostra")
        print("   - 's': pular classe atual") 
        print("   - 'q': sair do programa")
        print("-" * 50)
        
        for classe in todas_classes:
            print(f"\n🎯 Coletando dados para: {classe}")
            if not coletor.coletar_classe(classe):
                print("⏹️ Coleta interrompida pelo usuário")
                return
        
        # 2. Salvar dados coletados
        print("\n2. 💾 Salvando dados coletados...")
        coletor.salvar_dados()
        
        # 3. Treinar modelo
        print("\n3. 🧠 Fase de treinamento do modelo")
        classificador = ClassificadorLibras()
        
        if len(coletor.dados) > 0:
            print(f"📊 Dados disponíveis: {len(coletor.dados)} amostras")
            print(f"🏷️  Classes: {len(set(coletor.rotulos))}")
            
            precisao = classificador.treinar(coletor.dados, coletor.rotulos)
            
            if precisao > 0.8:
                print("✅ Modelo treinado com sucesso!")
                classificador.salvar_modelo()
                print("🎉 Treinamento concluído! Agora execute:")
                print("   python main_reconhecimento.py")
            else:
                print("⚠️  Precisão baixa. Considere coletar mais dados.")
        else:
            print("❌ Nenhum dado coletado para treinamento")
            
    except KeyboardInterrupt:
        print("\n🛑 Treinamento interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro durante treinamento: {e}")

if __name__ == "__main__":
    main()