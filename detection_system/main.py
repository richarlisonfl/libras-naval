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
from src.services.gerenciar_treinamento import GerenciadorTreinamento
from src.services.treino_sinais import TreinoSinais
from src.services.reconhecimento_hibrido import ReconhecimentoHibrido
from src.services.reconhecimento_navegador import ReconhecimentoNavegador


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
    print("4. Reconhecimento pela câmera do navegador")
    print("5. Sair")
    print("-" * 60)


def exibir_menu_treinamento():
    print("\n" + "-" * 60)
    print("MENU DE TREINAMENTO")
    print("-" * 60)
    print("1. Treinar um sinal estático")
    print("2. Treinar um sinal com movimento")
    print("3. Ver estatísticas dos sinais")
    print("4. Excluir um sinal gravado")
    print("5. Voltar ao Menu Principal")
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
    sinais = GerenciadorTreinamento.listar_sinais()
    if not sinais:
        print("\nNenhuma sessão de treinamento registrada.")
        return

    print("\nESTATÍSTICAS DOS SINAIS")
    print("-" * 60)
    for registro in sinais:
        pessoas = len(registro.get('pessoas', []))
        sessoes = registro.get('sessoes', 0)
        print(
            f"{registro['sinal']} ({registro['modo']}): "
            f"{sessoes} sessões, {pessoas} pessoas"
        )


def excluir_sinal_gravado():
    sinais = GerenciadorTreinamento.listar_sinais()
    if not sinais:
        print("\nNenhum sinal gravado para excluir.")
        return

    print("\nSINAIS GRAVADOS")
    print("-" * 60)
    for indice, registro in enumerate(sinais, start=1):
        print(f"{indice}. {registro['sinal']} ({registro['modo']})")

    escolha = input("\nNúmero do sinal a excluir: ").strip()
    if not escolha.isdigit() or not 1 <= int(escolha) <= len(sinais):
        print("Seleção inválida. Nenhum sinal foi excluído.")
        return

    registro = sinais[int(escolha) - 1]
    confirmacao = input(
        f"Digite EXCLUIR para remover {registro['sinal']} "
        f"({registro['modo']}): "
    ).strip()
    if confirmacao != "EXCLUIR":
        print("Exclusão cancelada.")
        return

    try:
        removidas = GerenciadorTreinamento().excluir_sinal(
            registro["modo"], registro["sinal"]
        )
        print(
            f"{removidas} amostra(s) de {registro['sinal']} removida(s). "
            "Os modelos disponíveis foram atualizados."
        )
    except (OSError, ValueError) as erro:
        print(f"Não foi possível excluir o sinal: {erro}")


def executar_reconhecimento():
    print("\n" + "-" * 60)
    print("RECONHECIMENTO EM TEMPO REAL")
    print("-" * 60)
    
    indice_camera = Camera.selecionar_indice_camera()
    if indice_camera is None:
        return
    
    try:
        resultado = ReconhecimentoHibrido(camera=indice_camera).executar()
        
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
        opcao = input("\nEscolha uma opção (1-5): ").strip()
        
        if opcao == "1":
            executar_treino_individual("estatico")
        elif opcao == "2":
            executar_treino_individual("dinamico")
        elif opcao == "3":
            exibir_estatisticas()
        elif opcao == "4":
            excluir_sinal_gravado()
        elif opcao == "5":
            print("Voltando ao menu principal...\n")
            break
        else:
            print(" Opção inválida! Tente novamente.")
        
        if opcao in ["1", "2", "3", "4"]:
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
            try:
                ReconhecimentoNavegador().executar()
            except Exception as erro:
                print(f"\n Erro no reconhecimento web: {erro}")
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
