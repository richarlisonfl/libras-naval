# 🤝 Sistema de Reconhecimento de LibrasNaval

Um sistema completo de reconhecimento de LIBRAS (Linguagem Brasileira de Sinais) Naval com suporte a treinamento e reconhecimento em tempo real.

## 📋 Características Principais

- **Menu Interativo**: Interface de linha de comando amigável
- **Treinamento com Webcam**: Captura de sinais em tempo real com índice de câmera configurável
- **Treinamento com Pastas**: Treinar com imagens organizadas em pastas (cada pasta = classe)
- **Reconhecimento em Tempo Real**: Detectar e classificar sinais de LIBRAS
- **Teste de Setup**: Verificar configuração de câmera e MediaPipe
- **Múltiplas Câmeras**: Suporte para múltiplas câmeras no sistema

## 🚀 Como Usar

### 1. Iniciar o Menu Principal

```bash
python main.py
```

Isso abrirá um menu interativo com as seguintes opções:

```
╔══════════════════════════════════════════════════════════╗
║   🤝 SISTEMA DE RECONHECIMENTO DE LibrasNaval         ║
╚══════════════════════════════════════════════════════════╝

📋 MENU PRINCIPAL
─────────────────────────────────────────────────────────
1. 🎯 Reconhecimento em Tempo Real
2. 🎓 Treinamento por sinal
3. 🔍 Teste de Setup (Câmera + MediaPipe)
4. 🚪 Sair
```

### 2. Opção 2: Treinamento por sinal

O fluxo recomendado treina um sinal por vez. Escolha uma das opções:

- Sinal estático: coleta amostras individuais.
- Sinal com movimento: coleta uma sequência de frames.
- Estatísticas: mostra sessões e pessoas registradas por sinal.

Use o mesmo nome do sinal e um identificador consistente para cada pessoa.
Novas sessões acumulam dados anteriores e podem reforçar somente os sinais com
baixo desempenho.

O treinamento com imagens por pastas permanece disponível apenas pelos scripts
individuais e não faz parte do menu principal.

### Fluxo antigo de treinamento

#### A. Treinar com Webcam

1. Selecione a opção `1 - Treinamento`
2. Selecione `1 - Treinar com Webcam`
3. O sistema procurará por câmeras disponíveis
4. Escolha o índice da câmera desejada
5. Escolha uma das opções de treinamento:
   - **Treinar apenas vogais (A E I O U)**: Começo rápido com 5 amostras cada
   - **Treinar meus próprios caracteres**: Digite as letras/números desejados
   - **Usar treinamento completo**: Treina todas as letras e números (mais demorado)

6. Para cada classe:
   - Posicione sua mão
   - Pressione ESPAÇO para capturar
   - Repeat até atingir a quantidade de amostras necessária
   - Pressione 's' para pular a classe
   - Pressione 'q' para sair

#### B. Treinar com Imagens de Pastas

1. Selecione a opção `1 - Treinamento`
2. Selecione `2 - Treinar com Imagens de Pastas`
3. Escolha o índice da câmera
4. Digite o caminho das pastas (padrão: `data/to_training`)

**Estrutura esperada:**

```
data/to_training/
├── A/
│   ├── imagem1.jpg
│   ├── imagem2.jpg
│   └── ...
├── B/
│   ├── imagem1.jpg
│   └── ...
└── ...
```

Cada pasta representa uma **classe/label** para treinamento. O sistema:
- Processa todas as imagens em cada pasta
- Detecta as mãos usando MediaPipe
- Extrai características dos landmarks
- Treina um modelo com todas as amostras

### Fluxo auxiliar: Capturar Imagens para Treinamento

Uma forma rápida e organizada de coletar imagens para treinar o modelo:

1. Selecione a opção `2 - Capturar Imagens para Treinamento`
2. Escolha o índice da câmera
3. O sistema detectará automaticamente as pastas de classes em `data/to_training/`
4. Para cada classe:
   - Posicione seu sinal na câmera
   - Pressione **ESPAÇO** para capturar a imagem
   - Cada imagem é salva como `{classe}_{contador:04d}.jpg`
   - Pressione **ENTER** para avançar para a próxima classe
   - Pressione **R** para reiniciar o contador da classe atual
   - Pressione **Q** para sair

**Interface de Captura:**

```
┌─────────────────────┐
│ CLASSE: A           │  ← Classe atual
│ Imagens: 15         │  ← Quantas imagens já foram capturadas
│ Classe 1/5          │  ← Progresso entre classes
│ ESPACO: Capturar    │  ← Instruções
│ ENTER: Proxima      │
│ R: Reset | Q: Sair  │
└─────────────────────┘
```

**Vantagens:**
- ✅ Imagens salvas **limpas** (sem texto ou anotações)
- ✅ Organisadas automaticamente por classe
- ✅ Contador automático com nome sequencial
- ✅ Interface compacta no canto superior esquerdo
- ✅ Ideal para coletar dados de treinamento antes de usar a opção "Treinar com Imagens de Pastas"

### 3. Opção 1: Reconhecimento em Tempo Real

1. Selecione a opção `3 - Reconhecimento em Tempo Real`
2. Escolha o índice da câmera
3. O sistema carregará o modelo treinado
4. Mostre seus sinais de LIBRAS para o programa
5. Pressione 'q' para sair

**Interface de Reconhecimento:**
- **SINAL**: Classificação atual (letra/número reconhecido)
- **CONFIANÇA**: Valor de 0.0 a 1.0 indicando a segurança da previsão
- **STATUS**: Indicação visual de Alta/Média/Baixa/Muito Baixa confiança
- Barra visual mostrando o nível de confiança
- **SUAVIZADO**: Previsão suavizada com base no histórico

### 4. Opção 3: Teste de Setup

Verifica se a câmera e o MediaPipe estão funcionando corretamente.

## 📁 Estrutura de Arquivos

```
libras-naval/
├── main.py                              # Menu principal
├── config.py                            # Configurações globais
├── requirements.txt                     # Dependências
└── src/
   ├── apps/
   │   ├── capturador_imagens.py        # Captura de imagens
   │   ├── treinamento_app.py           # Treinamento
   │   └── reconhecimento_app.py        # Reconhecimento
   ├── core/
   │   ├── camera.py                    # Acesso à câmera
   │   ├── detector_maos.py             # Detecção e landmarks
   │   ├── classificador.py             # Classificador ML
   │   └── coletor_dados.py             # Coleta de características
   ├── services/
   │   ├── reconhecedor.py              # Reconhecimento em tempo real
   │   ├── treinamento_incremental.py   # Treinamento incremental
   │   └── websocket.py                 # Comunicação WebSocket
   └── tools/
      ├── teste_rapido.py              # Teste de setup
      ├── validar_sistema.py           # Validação completa
      └── verificar_sistema.py         # Verificação rápida
├── data/
│   ├── to_training/                     # Imagens (ignoradas pelo Git)
│   └── generated_model/                 # Artefatos versionáveis
│       ├── modelo_libras.pkl
│       └── dados_libras.npz
└── README.md                            # Este arquivo
```

## 🛠️ Configuração

### Instalação de Dependências

```bash
python -m pip install -r requirements.txt
```

Dependências necessárias:
- `opencv-contrib-python`: Processamento de imagens
- `mediapipe`: Detecção de landmarks das mãos pela API Tasks
- `scikit-learn`: Classificação de dados
- `numpy`: Operações numéricas

O primeiro uso do sistema baixa automaticamente os modelos `hand_landmarker.task`,
`gesture_recognizer.task` e `pose_landmarker_lite.task` para `models/`. Para usar
um arquivo já baixado, defina
`MEDIAPIPE_HAND_LANDMARKER_MODEL` com o caminho completo do modelo antes de
executar o sistema.

O teste de setup combina `Hand Landmarker`, `Gesture Recognizer` e `Pose
Landmarker`. Ele mostra landmarks das mãos, lado e orientação, gesto
pré-treinado e a quantidade de landmarks corporais detectados. Esses recursos
servem para diagnóstico; o reconhecimento dos sinais de Libras continua sendo
feito pelos modelos treinados do projeto.

O treinamento salva o modelo em `data/generated_model/modelo_libras.pkl` e as
características numéricas em `data/generated_model/dados_libras.npz`. As
imagens permanecem ignoradas pelo Git, mas esses dois artefatos podem ser
versionados. O arquivo `.npz` permite continuar o treinamento de forma
incremental sem as imagens anteriores.

### Arquivo de Configuração (config.py)

Você pode ajustar as seguintes configurações:

```python
CONFIG = {
    'dimensao_imagem': (640, 480),           # Resolução da câmera
    'numero_amostras_por_classe': 20,        # Amostras por classe no treinamento
   'caminho_dados': 'data/to_training',     # Pasta de imagens
    'limite_confianca': 0.6,                 # Limite mínimo de confiança
}
```

## 🎯 Uso Avançado

### Usar Scripts Individualmente

#### Capturar Imagens para Treinamento

```bash
python src/apps/capturador_imagens.py --camera 0
```

#### Treinamento com Webcam

```bash
python src/apps/treinamento_app.py --camera 0 --modo webcam
```

#### Treinamento com Pastas

```bash
python src/apps/treinamento_app.py --camera 0 --modo pastas --caminho data/to_training
```

#### Reconhecimento

```bash
python src/apps/reconhecimento_app.py --camera 0
```

### Parâmetros de Linha de Comando

**src/apps/capturador_imagens.py:**
- `--camera N`: Índice da câmera (padrão: 0)
- `--caminho CAMINHO`: Caminho para pasta de classes (padrão: data/to_training)

**src/apps/treinamento_app.py:**
- `--camera N`: Índice da câmera (padrão: 0)
- `--modo [webcam|pastas]`: Modo de treinamento (padrão: webcam)
- `--caminho CAMINHO`: Caminho para pasta de imagens (padrão: data/to_training)

**src/apps/reconhecimento_app.py:**
- `--camera N`: Índice da câmera (padrão: 0)

## 📊 Fluxo de Funcionamento

```
┌─────────────────────────────────────────────────────┐
│        Menu Principal (main.py)                    │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬───────────────┐
        │               │               │               │
    ┌───▼────┐    ┌─────▼──────┐ ┌─────▼────┐    ┌─────▼────┐
    │ TREINAR│    │ CAPTURADOR │ │RECONHECER│    │TESTE     │
    └───┬────┘    └─────┬──────┘ └──────┬───┘    └──────┬───┘
        │                │              │              │
    ┌───▼────────┐       │         ┌────▼──────────┐   │
    │            │       │         │Carrega modelo │   │
┌───▼──┐   ┌────▼──┐   ┌┴──────────┤────┬─────────┘   │
│Webcam│   │Pastas │   │Salva      │    │         (testa câmera)
└────┬─┘   └──┬────┘   │imagem     │    │
     │        │        └──────────┘    │
     ├────────┤                        │
     │        │    ┌───────────────────┘
     │        │    │
  ┌──▼──────────────▼──────────────┐
  │Extrai landmarks da imagem      │
  └──┬───────────────────────────┘
     │
  ┌──▼──────────────────────────┐
  │Treina/Classifica modelo     │
  └──┬─────────────────────────┘
     │
  ┌──▼──────────────────────────┐
  │Salva modelo                 │
  └──┬────────────────────────┬─┘
     │                        │
     │         ┌──────────────┘
     │         │
     └────────►├─ Faz previsões
               │
               └─ Exibe resultado
```

## 🐛 Troubleshooting

### Câmera não encontrada

- Verifique se a câmera está conectada
- Tente diferentes índices de câmera (0, 1, 2, ...)
- Use o comando `test_rapido.py` para testar

### MediaPipe não detecta a mão

- Garanta boa iluminação
- Posicione a mão no centro da câmera
- Certifique-se de que a mão está completamente visível

### Modelo não encontrado

- Execute o treinamento primeiro
- Verifique se o arquivo `data/generated_model/modelo_libras.pkl` existe

### Baixa precisão de reconhecimento

- Capture mais amostras de treinamento
- Garanta que o ambiente de iluminação seja semelhante durante treinamento e reconhecimento
- Treine com diferentes ângulos e posições

## 📝 Exemplos de Uso

### Exemplo 1: Capturar Imagens para Treinamento

```bash
# Opção 1: Via menu principal
python main.py
# Selecione: 2 - Capturar Imagens para Treinamento

# Opção 2: Diretamente
python capturador_imagens.py --camera 0
```

Instrações:
- Crie pastas em `data/to_training/` com nomes das classes (ex: A, B, C)
- Execute o capturador
- Para cada classe, pressione ESPAÇO para capturar
- Pressione ENTER para ir para a próxima classe
- As imagens serão salvas limpas (sem anotações)

### Exemplo 2: Treinar com Imagens Capturadas

```bash
python main.py
# Selecione: 1 - Treinamento
# Selecione: 2 - Treinar com Imagens de Pastas
# Digite: data/to_training (as imagens que você capturou)
```

### Exemplo 3: Treinamento Rápido de Vogais

```bash
python main.py
# Selecione: 1 - Treinamento
# Selecione: 1 - Treinar com Webcam
# Selecione: 1 - Treinar apenas vogais
# Complete o treinamento
```

### Exemplo 4: Treinamento com Seus Próprios Dados

1. Organize imagens em pastas:
   ```
   meus_dados/
   ├── A/
   ├── B/
   ├── C/
   └── ...
   ```

2. Execute:
   ```bash
   python main.py
   # Selecione: 1 - Treinamento
   # Selecione: 2 - Treinar com Imagens de Pastas
   # Digite: meus_dados
   ```

### Exemplo 5: Usar Câmera Específica

```bash
# Se você tem múltiplas câmeras
python main.py
# Quando solicitado, escolha o índice correto da câmera
```

## 🤝 Contribuindo

Para contribuir com melhorias, siga os padrões de código existentes e adicione testes quando possível.

## 📜 Licença

Este projeto está sob a licença [MIT](LICENSE).

## 👥 Autores

- Desenvolvido para o Sistema de LibrasNaval

## 🙏 Agradecimentos

- MediaPipe por fornecer a detecção de landmarks
- OpenCV pela captura e processamento de vídeo
- Scikit-learn pelos algoritmos de classificação
