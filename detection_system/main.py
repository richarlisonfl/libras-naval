#!/usr/bin/env python3
import os
import sys
import subprocess
import time

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "0"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TFLITE_DEBUG_LOG_LEVEL"] = "0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

import config
from src.core.camera import Camera
from src.apps.capturador_imagens import CapturadorImagens
from src.apps.reconhecimento_app import ReconhecimentoApp
from src.apps.treinamento_app import TreinamentoApp
from src.services.treinamento_incremental import TreinamentoIncremental


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
    print("1. Reconhecimento em Tempo Real")
    print("2. Treinamento")
    print("3. Capturar Imagens para Treinamento")
    print("4. Teste de Setup (Câmera + MediaPipe)")
    print("5. Sair")
    print("-" * 60)


def exibir_menu_treinamento():
    print("\n" + "-" * 60)
    print("MENU DE TREINAMENTO")
    print("-" * 60)
    print("1. Treinar com Webcam (Captura ao vivo)")
    print("2. Treinar com Imagens de Pastas (cada pasta = classe)")
    print("3. Treinamento incremental")
    print("4. Voltar ao Menu Principal")
    print("-" * 60)


def pausar_menu(mensagem="\nPressione ENTER para voltar ao menu principal..."):
    input(mensagem)


def executar_treinamento_webcam():
    print("\n" + "-" * 60)
    print("TREINAMENTO COM WEBCAM")
    print("-" * 60)
    
    indice_camera = Camera.selecionar_indice_camera()
    if indice_camera is None:
        return
    
    try:
        treinamento = TreinamentoApp(camera=indice_camera)
        resultado = treinamento.run("webcam")

        if resultado:
            print("\n Treinamento completado com sucesso!")
        else:
            print("\n Erro durante o treinamento.")
            
    except Exception as e:
        print(f"\n Erro ao executar treinamento: {e}")


def executar_treinamento_pastas():
    print("\n" + "-" * 60)
    print("TREINAMENTO COM IMAGENS DE PASTAS")
    print("-" * 60)
    
    caminho_dados = input(f"\nDigite o caminho das pastas (deixe vazio para utilizar o caminho padrão: {config.CONFIG['caminho_dados']}): ").strip()
    if not caminho_dados:
        caminho_dados = config.CONFIG['caminho_dados']
    
    if not os.path.exists(caminho_dados):
        print(f" Caminho '{caminho_dados}' não encontrado!")
        return
    
    try:
        treinamento = TreinamentoApp()
        resultado = treinamento.run("pastas", caminho_dados)

        if resultado:
            print("\n Treinamento completado com sucesso!")
        else:
            print("\n Erro durante o treinamento.")
            
    except Exception as e:
        print(f"\n Erro ao executar treinamento: {e}")


def executar_treinamento_incremental():
    print("\n" + "-" * 60)
    print("TREINAMENTO INCREMENTAL")
    print("-" * 60)

    try:
        treinamento = TreinamentoIncremental()
        treinamento.treinar_por_fases()
    except Exception as e:
        print(f"\n Erro ao executar treinamento incremental: {e}")


def executar_reconhecimento():
    print("\n" + "-" * 60)
    print("RECONHECIMENTO EM TEMPO REAL")
    print("-" * 60)
    
    indice_camera = Camera.selecionar_indice_camera()
    if indice_camera is None:
        return
    
    try:
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
        resultado = subprocess.run(
            [sys.executable, os.path.join(BASE_DIR, 'src', 'tools', 'teste_rapido.py')],
            cwd=BASE_DIR,
            check=False,
        )
        
        if resultado.returncode == 0:
            print("\n Teste concluído!")
        else:
            print("\n  Teste interrompido.")
            
    except Exception as e:
        print(f"\n Erro ao executar teste: {e}")


def execute_images_capture():
    print("\n" + "-" * 60)
    print("CAPTURADOR DE IMAGENS")
    print("-" * 60)
    
    indice_camera = Camera.selecionar_indice_camera()
    if indice_camera is None:
        return
    
    try:
        capturador = CapturadorImagens(str(config.CONFIG['caminho_dados']), str(indice_camera))

        if capturador.classes:
            capturador.capturar()
            print("\n Captura concluída com sucesso!")
        else:
            print(" Nenhuma classe encontrada. Crie as pastas primeiro.")
            print("\n  Captura interrompida.")
            sys.exit(1)

    except Exception as e:
        print(f"\n Erro ao executar captura: {e}")


def menu_treinamento():
    while True:
        exibir_menu_treinamento()
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == "1":
            executar_treinamento_webcam()
        elif opcao == "2":
            executar_treinamento_pastas()
        elif opcao == "3":
            executar_treinamento_incremental()
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
        
        opcao = input("Escolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            executar_reconhecimento()
            pausar_menu()
        elif opcao == "2":
            menu_treinamento()
        elif opcao == "3":
            execute_images_capture()
            pausar_menu()
        elif opcao == "4":
            executar_teste_setup()
            pausar_menu()
        elif opcao == "5":
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
