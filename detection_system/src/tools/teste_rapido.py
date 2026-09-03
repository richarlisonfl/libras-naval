#!/usr/bin/env python3
"""Verifica a câmera e o detector de mãos MediaPipe."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import cv2

from src.core.detector_maos import DetectorMaos

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


def desenhar_informacoes(imagem, resultados, detector, tempo_ms, fps):
    """Exibe métricas e desenha os landmarks detectados."""
    cv2.putText(imagem, f"MediaPipe 1.x | FPS: {fps:.1f} | {tempo_ms:.1f} ms",
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    cv2.putText(imagem, f"Maos detectadas: {len(resultados.multi_hand_landmarks)}",
                (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    for indice, marcos_mao in enumerate(resultados.multi_hand_landmarks):
        detector.desenhar_landmarks(imagem, marcos_mao)
        lado = None
        if indice < len(resultados.multi_handedness):
            lado = resultados.multi_handedness[indice][0].category_name
        orientacao, confianca_orientacao = detector.estimar_orientacao(
            marcos_mao, lado
        )
        texto_orientacao = (
            f"Orientacao {indice + 1}: {orientacao} "
            f"({confianca_orientacao:.0%})"
        )
        cv2.putText(imagem, texto_orientacao, (10, 125 + indice * 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)
        for numero, ponto in enumerate(marcos_mao.landmark):
            x = int(ponto.x * imagem.shape[1])
            y = int(ponto.y * imagem.shape[0])
            cv2.putText(imagem, str(numero), (x + 4, y - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)

        if indice < len(resultados.multi_handedness):
            classificacao = resultados.multi_handedness[indice][0]
            texto = f"{classificacao.category_name}: {classificacao.score:.1%}"
            cv2.putText(imagem, texto, (10, 75 + indice * 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)


def testar_captura(camera, detector):
    """Processa frames até o usuário pressionar a tecla q."""
    print(" Testando captura. Pressione 'q' para encerrar...")

    mao_detectada_anteriormente = False
    cv2.namedWindow(NOME_JANELA, cv2.WINDOW_NORMAL)

    while True:
        sucesso, imagem = camera.read()
        if not sucesso:
            print(" Erro ao ler imagem da câmera")
            return False

        imagem = cv2.flip(imagem, 1)
        inicio = cv2.getTickCount()
        resultados = detector.maos.process(
            cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        )
        tempo_ms = (cv2.getTickCount() - inicio) * 1000 / cv2.getTickFrequency()
        fps = camera.get(cv2.CAP_PROP_FPS) or 0.0
        desenhar_informacoes(imagem, resultados, detector, tempo_ms, fps)

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
        detector = DetectorMaos()
        print(" MediaPipe carregado com sucesso!")
        testar_captura(camera, detector)
        return 0
    except Exception as erro:
        print(f" Erro no MediaPipe: {erro}")
        return 1
    finally:
        camera.release()
        cv2.destroyWindow(NOME_JANELA)
        print(" Teste concluído!")


if __name__ == "__main__":
    raise SystemExit(main())