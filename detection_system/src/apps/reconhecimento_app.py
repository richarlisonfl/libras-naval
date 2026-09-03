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

# Permite execução direta pelo terminal.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.core.camera import Camera


def parse_args():
    """Parse de argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Reconhecimento de LIBRAS - versão adaptada')
    parser.add_argument('--camera', type=int, default=0, help='Índice da câmera (padrão: 0)')
    return parser.parse_args()


class ReconhecimentoApp:
    """Classe que encapsula o fluxo de reconhecimento para uso por outros scripts.

    Exemplo:
        app = ReconhecimentoApp(camera=0)
        app.run()
    """

    def __init__(self, camera: int = 0):
        self.camera = int(camera)
        self.reconhecedor = None

    def _load_components(self) -> bool:
        """Carrega os componentes necessários e o modelo.

        Retorna True se o modelo foi carregado com sucesso.
        """
        from src.services.reconhecedor import ReconhecedorLibras

        print(" Carregando componentes...")
        self.reconhecedor = ReconhecedorLibras(indice_camera=self.camera)

        print(" Carregando modelo treinado...")
        return self.reconhecedor.carregar_modelo()

    def run(self):
        """Executa o fluxo de reconhecimento (carregamento + execução)."""
        print(" RECONHECIMENTO DE LIBRAS")
        print(f" Usando câmera: índice {self.camera}")
        print("-" * 60)

        try:
            loaded = self._load_components()
            if loaded:
                print(f" Modelo carregado - {len(self.reconhecedor.classificador.decoder_rotulos)} classes")
                print(" Iniciando câmera em 3 segundos...")
                print(" Mostre os sinais para testar!")
                import time
                time.sleep(3)
                self.reconhecedor.executar_reconhecimento()
            else:
                print(" Modelo não encontrado!")
                print(" Execute: python main.py (e selecione a opção de treinamento)")
            return True
        except KeyboardInterrupt:
            print("\n Programa finalizado pelo usuário")
            return False
        except Exception as e:
            print(f" Erro inesperado: {e}")
            print("\n Detalhes do erro:")
            traceback.print_exc()
            return False


def main():
    """Função principal usada quando o script é executado diretamente."""
    args = parse_args()
    indice_camera = Camera.selecionar_indice_camera()
    if indice_camera is None:
        camera_index = args.camera
    else:
        camera_index = indice_camera

    app = ReconhecimentoApp(camera=camera_index)
    app.run()


if __name__ == "__main__":
    main()
