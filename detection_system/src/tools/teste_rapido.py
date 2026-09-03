#!/usr/bin/env python3
"""Verifica a câmera e o detector de mãos MediaPipe."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2

from sistema_libras.utilitarios import UtilitariosMaos

INDICES_CAMERA = range(5)
NOME_JANELA = "Teste Câmera"


def abrir_camera():
    """Abre a primeira câmera disponível."""
    print(" Testando câmera...")

    for indice in INDICES_CAMERA:
        camera = cv2.VideoCapture(indice)
        if camera.isOpened():
            print(f" Câmera {indice} funcionando!")
            return camera
        camera.release()

    print(" Não foi possível abrir nenhuma câmera.")
    return None


def testar_captura(camera, utilitarios):
    """Processa frames até o usuário pressionar a tecla q."""
    print(" Testando captura. Pressione 'q' para encerrar...")

    mao_detectada_anteriormente = False
    while True:
        sucesso, imagem = camera.read()
        if not sucesso:
            print(" Erro ao ler imagem da câmera")
            return False

        imagem = cv2.flip(imagem, 1)
        resultados = utilitarios.maos.process(
            cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        )

        cv2.imshow(NOME_JANELA, imagem)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            return True

        mao_detectada = bool(resultados.multi_hand_landmarks)
        if mao_detectada and not mao_detectada_anteriormente:
            print(" Mão detectada!")
        mao_detectada_anteriormente = mao_detectada


def main():
    camera = abrir_camera()
    if camera is None:
        return 1

    try:
        print(" Testando MediaPipe...")
        utilitarios = UtilitariosMaos()
        print(" MediaPipe carregado com sucesso!")
        testar_captura(camera, utilitarios)
        return 0
    except Exception as erro:
        print(f" Erro no MediaPipe: {erro}")
        return 1
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print(" Teste concluído!")


if __name__ == "__main__":
    raise SystemExit(main())