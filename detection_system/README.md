# Sistema de Reconhecimento de LIBRAS

O sistema coleta sinais diretamente da camera, extrai landmarks das maos com MediaPipe e treina classificadores `SVC` do scikit-learn.

## Execucao

```bash
cd detection_system
.venv/bin/python main.py
```

O menu oferece reconhecimento hibrido, treinamento de sinais e teste de camera/MediaPipe.

## Treinamento

O treinamento e feito pelo menu, um sinal por sessao:

- **Estatico:** captura amostras individuais de uma posicao da mao.
- **Dinamico:** captura uma sequencia de frames de um movimento.

As imagens nao sao salvas como dataset. Cada frame e processado imediatamente pelo MediaPipe e convertido em 68 caracteristicas:

```text
21 landmarks x 3 coordenadas = 63
4 angulos dos dedos = 4
1 componente de orientacao = 1
Total = 68 caracteristicas
```

Sao necessarias pelo menos duas classes para gerar um modelo. Os arquivos gerados ficam em `data/generated_model/`:

- `modelo_libras.pkl` e `dados_libras.npz` para sinais estaticos;
- `modelo_dinamico.pkl` e `sequencias_libras.npz` para sinais dinamicos;
- `catalogo_treinamento.json` com o registro das sessoes.

## Reconhecimento hibrido

O sistema usa uma unica captura da camera e carrega os modelos disponiveis:

- mao estavel: prioriza o modelo estatico;
- movimento detectado: prioriza o modelo dinamico;
- resultado confiavel: envia o sinal ao jogo pelo WebSocket.

## Validacao

```bash
.venv/bin/python -m py_compile main.py config.py src/**/*.py
.venv/bin/python src/tools/validar_sistema.py
```

O sistema precisa de Python 3.11, OpenCV, MediaPipe, NumPy, scikit-learn, websockets e um ambiente grafico para as janelas da camera.
