# Sistema de Reconhecimento de LibrasNaval

Sistema para treinamento e reconhecimento de sinais de LIBRAS em tempo real, integrado a interface do jogo por WebSocket.

## Requisitos

- Python 3.11
- Node.js e npm
- Camera compativel com OpenCV
- Ambiente grafico para as janelas da camera

O detector usa MediaPipe Tasks e o treinamento usa scikit-learn.

## Instalacao e execucao Linux

```bash
chmod +x linux_start_game.sh
./linux_start_game.sh
```

Tambem e possivel executar somente o sistema Python:

```bash
cd detection_system
.venv/bin/python main.py
```

O menu oferece:

1. Reconhecimento hibrido em tempo real
2. Treinamento estatico ou dinamico
3. Teste de camera e MediaPipe
4. Saida

## Treinamento

O treinamento atual nao usa imagens salvas em pastas. Os frames sao capturados pela camera, processados imediatamente pelo MediaPipe e convertidos em landmarks, angulos e orientacao da mao.

- **Estatico:** uma amostra por captura, para posicoes paradas.
- **Dinamico:** uma sequencia de frames, para sinais com movimento.

Treine pelo menos duas classes de cada tipo antes de usar o respectivo modelo. Os dados numericos e modelos ficam em `detection_system/data/generated_model/`.

## Reconhecimento hibrido

Durante o jogo, o sistema analisa os dois tipos sem pedir uma selecao previa:

```text
camera -> MediaPipe -> landmarks -> modelos estatico e dinamico -> WebSocket -> jogo
```

Uma mao estavel favorece o modelo estatico; um movimento detectado favorece o modelo dinamico. Os limites podem ser ajustados em [detection_system/config.py](detection_system/config.py).

## Windows

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\\windows_start_game.ps1
```

## Validacao

```bash
cd detection_system
.venv/bin/python -m py_compile main.py config.py src/**/*.py
.venv/bin/python src/tools/validar_sistema.py
```
