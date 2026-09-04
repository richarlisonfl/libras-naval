#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import json

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "0"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TFLITE_DEBUG_LOG_LEVEL"] = "0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import config
from src.core.camera import Camera
from src.apps.reconhecimento_app import ReconhecimentoApp
from src.services.treino_sinais import TreinoSinais
from src.services.reconhecimento_dinamico import ReconhecimentoDinamico


def limpar_tela():
    os.system("clear" if os.name == "posix" else "cls")


def exibir_banner():
    print("\n" + "=" * 60)
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  SISTEMA DE RECONHECIMENTO DE LIBRASNAVAL   ".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("=" * 60 + "\n")


def exibir_menu_principal():
    print("\n" + "-" * 60)
    print("MENU PRINCIPAL")
    print("-" * 60)
    print("1. Reconhecimento")
    print("2. Treinamento")
    print("3. Teste de Setup (Câmera + MediaPipe)")
    print("4. Sair")
    print("-" * 60)


def exibir_menu_treinamento():
    print("\n" + "-" * 60)
    print("MENU DE TREINAMENTO")
    print("-" * 60)
    print("1. Treinar um sinal estático")
    print("2. Treinar um sinal com movimento")
    print("3. Ver estatísticas dos sinais")
    print("4. Voltar ao Menu Principal")
    print("-" * 60)


def pausar_menu(mensagem="\nPressione ENTER para voltar ao menu principal..."):
    input(mensagem)


def executar_treino_individual(modo):
    nome_modo = "estático" if modo == "estatico" else "dinâmico"
    print(f"\nTREINAR UM SINAL {nome_modo.upper()}")
    sinal = input("Nome do sinal (ex.: A ou J): ").strip().upper()
    pessoa = input("Identificador da pessoa: ").strip()
    padrao = 100 if modo == "estatico" else 45
    unidade = "frames capturados" if modo == "dinamico" else "amostras"
    valor = input(f"Quantidade ({padrao} {unidade}): ").strip()
    quantidade = int(valor) if valor.isdigit() and int(valor) > 0 else padrao

    try:
        indice_camera = Camera.selecionar_indice_camera()
        if indice_camera is None:
            return
        resultado = TreinoSinais(indice_camera).executar(
            modo, sinal, quantidade, pessoa
        )
        if resultado is None:
            print("Dados salvos; outro sinal é necessário para gerar o modelo.")
        else:
            print(f"Treinamento concluído. Precisão: {resultado:.3%}")
    except Exception as erro:
        print(f"Erro no treinamento do sinal: {erro}")


def exibir_estatisticas():
    caminho = os.path.join(config.CONFIG['caminho_modelos'], 'catalogo_treinamento.json')
    if not os.path.exists(caminho):
        print("\nNenhuma sessão de treinamento registrada.")
        return

    with open(caminho, encoding='utf-8') as arquivo:
        catalogo = json.load(arquivo)

    print("\nESTATÍSTICAS DOS SINAIS")
    print("-" * 60)
    for registro in catalogo.values():
        pessoas = len(registro.get('pessoas', []))
        sessoes = registro.get('sessoes', 0)
        print(
            f"{registro['sinal']} ({registro['modo']}): "
            f"{sessoes} sessões, {pessoas} pessoas"
        )


def executar_reconhecimento():
    print("\n" + "-" * 60)
    print("RECONHECIMENTO EM TEMPO REAL")
    print("-" * 60)
    
    indice_camera = Camera.selecionar_indice_camera()
    if indice_camera is None:
        return
    
    try:
        modo = input("Escolha o modo (1-estático, 2-dinâmico): ").strip()
        if modo == "2":
            resultado = ReconhecimentoDinamico(camera=indice_camera).executar()
            print("\n Reconhecimento dinâmico finalizado!" if resultado else "\n Modelo dinâmico indisponível.")
            return

        reconhecimento = ReconhecimentoApp(camera=indice_camera)
        resultado = reconhecimento.run()
        
        if resultado:
            print("\n Reconhecimento finalizado!")
        else:
            print("\n  Reconhecimento interrompido.")
            
    except Exception as e:
        print(f"\n Erro ao executar reconhecimento: {e}")


def executar_teste_setup():
    print("\n" + "-" * 60)
    print("TESTE DE SETUP")
    print("-" * 60)
    
    try:
        indice_camera = Camera.selecionar_indice_camera()
        if indice_camera is None:
            return
        resultado = subprocess.run(
            [
                sys.executable,
                os.path.join(BASE_DIR, 'src', 'tools', 'teste_rapido.py'),
                '--camera',
                str(indice_camera),
            ],
            cwd=BASE_DIR,
            check=False,
        )
        
        if resultado.returncode == 0:
            print("\n Teste concluído!")
        else:
            print("\n  Teste interrompido.")
            
    except Exception as e:
        print(f"\n Erro ao executar teste: {e}")


def menu_treinamento():
    while True:
        exibir_menu_treinamento()
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            executar_treino_individual("estatico")
        elif opcao == "2":
            executar_treino_individual("dinamico")
        elif opcao == "3":
            exibir_estatisticas()
        elif opcao == "4":
            print("Voltando ao menu principal...\n")
            break
        else:
            print(" Opção inválida! Tente novamente.")
        
        if opcao in ["1", "2", "3"]:
            pausar_menu("\nPressione ENTER para voltar ao menu de treinamento...")


def menu_principal():
    while True:
        limpar_tela()
        exibir_banner()
        exibir_menu_principal()
        
        opcao = input("Escolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            executar_reconhecimento()
            pausar_menu()
        elif opcao == "2":
            menu_treinamento()
        elif opcao == "3":
            executar_teste_setup()
            pausar_menu()
        elif opcao == "4":
            print("\n" + "="*60)
            print("Obrigado por usar o Sistema de LibrasNaval!")
            print("="*60 + "\n")
            break
        else:
            print(" Opção inválida! Tente novamente.")
            time.sleep(2)


def main():
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n Programa interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
