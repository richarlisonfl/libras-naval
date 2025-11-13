#!/usr/bin/env python3
"""
Treinamento facilitado - versão simplificada e funcional
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sistema_libras.coletor_dados import ColetorDadosLibras
from sistema_libras.classificador import ClassificadorLibras
import config

def treinar_apenas_estas_classes(classes, amostras_por_classe=5):
    """Treina apenas as classes especificadas"""
    print(f"🎯 Treinando: {classes}")
    print(f"📸 Amostras por classe: {amostras_por_classe}")
    print("-" * 50)
    
    # Configurar número reduzido de amostras
    config_original = config.CONFIG['numero_amostras_por_classe']
    config.CONFIG['numero_amostras_por_classe'] = amostras_por_classe
    
    coletor = ColetorDadosLibras()
    
    for classe in classes:
        print(f"\n📝 Classe atual: {classe}")
        print("💡 Posicione a mão e pressione ESPAÇO para capturar")
        print("   Pressione 's' para pular esta classe")
        print("   Pressione 'q' para sair")
        print("-" * 30)
        
        if not coletor.coletar_classe(classe):
            print("⏹️ Coleta interrompida")
            return False
    
    # Restaurar configuração original
    config.CONFIG['numero_amostras_por_classe'] = config_original
    
    # Treinar modelo
    if len(coletor.dados) > 0:
        print(f"\n🧠 Treinando modelo com {len(coletor.dados)} amostras...")
        classificador = ClassificadorLibras()
        precisao = classificador.treinar(coletor.dados, coletor.rotulos)
        classificador.salvar_modelo()
        print(f"✅ Modelo treinado! Precisão: {precisao:.3f}")
        return True
    else:
        print("❌ Nenhum dado coletado")
        return False

def main():
    print("🎓 TREINAMENTO FACILITADO DE LIBRAS")
    print("=" * 50)
    print("💡 Vamos começar com poucas letras!")
    print("=" * 50)
    
    try:
        print("\nEscolha uma opção fácil:")
        print("1. Treinar apenas vogais (A E I O U) - 5 amostras cada")
        print("2. Treinar meus próprios caracteres")
        print("3. Usar treinamento completo (original)")
        
        opcao = input("\nDigite sua opção (1-3): ").strip()
        
        if opcao == "1":
            # Opção mais fácil: apenas vogais
            sucesso = treinar_apenas_estas_classes("AEIOU", 5)
            if sucesso:
                print("\n🎉 Parabéns! Você treinou as vogais!")
                print("👉 Agora teste com: python main_reconhecimento.py")
                
        elif opcao == "2":
            letras = input("Digite as letras/números (ex: ABC123): ").strip().upper()
            if letras:
                amostras = input("Amostras por classe (padrão 5): ").strip()
                amostras = int(amostras) if amostras.isdigit() else 5
                treinar_apenas_estas_classes(letras, amostras)
            else:
                print("❌ Nenhum caractere digitado")
                
        elif opcao == "3":
            # Usar o treinamento original
            from main_treinamento import main as treinamento_original
            treinamento_original()
            
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n🛑 Programa interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()