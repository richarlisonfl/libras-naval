# Sistema de Reconhecimento de LIBRAS Naval

Sistema para captura de imagens, treinamento e reconhecimento de sinais de LIBRAS em tempo real. O projeto possui uma aplicação Python de visão computacional e um servidor Node.js usado pela interface do jogo.

## Requisitos

- Python 3.11
- Node.js e npm
- Uma câmera compatível com OpenCV
- Linux ou Windows
- Ambiente gráfico para abrir as janelas do OpenCV

O código atual usa a API `mediapipe.solutions`. Por isso, a versão compatível é:

```text
mediapipe==0.10.14
```

Não substitua essa versão por `mediapipe 1.x` sem adaptar o código de detecção de mãos.

## Estrutura principal

```text
libras-naval/
├── computer_vision/
│   ├── .venv/                  # Ambiente Python principal
│   ├── venv_atualizado/        # Ambiente opcional para testes
│   ├── main.py                 # Menu principal
│   ├── config.py               # Configurações e caminhos
│   ├── requirements.txt        # Dependências Python
│   ├── data/
│   │   ├── to_training/        # Imagens organizadas por classe
│   │   └── generated_model/    # Modelo treinado
│   └── src/
│       ├── camera.py
│       ├── capturador_imagens.py
│       ├── reconhecimento_app.py
│       ├── treinamento_app.py
│       └── sistema_libras/
├── game_interface/             # Interface do jogo
├── game_server/                # Servidor Node.js
├── linux_start_game.sh         # Inicializador Linux
├── windows_start_game.ps1      # Inicializador Windows PowerShell
└── README.md
```

## Instalação Linux

A forma recomendada é usar o inicializador do projeto:

```bash
chmod +x linux_start_game.sh
./linux_start_game.sh
```

O script:

1. Verifica se o Python 3.11 está disponível.
2. Cria `computer_vision/.venv` caso necessário.
3. Instala as dependências Python.
4. Instala as dependências do servidor Node.js.
5. Inicia o servidor e o reconhecimento.

Se o Python 3.11 não estiver instalado, o script tenta instalá-lo usando `sudo` e compilação local. Nesse caso, será necessária uma conexão com a internet e uma conta autorizada a usar `sudo`.

## Execução manual Linux

```bash
cd computer_vision
source .venv/bin/activate
python main.py
```

Também é possível executar sem ativar o ambiente:

```bash
cd computer_vision
.venv/bin/python main.py
```

Não execute `python main.py` na raiz do projeto, pois o arquivo está dentro de `computer_vision`.

## Instalação e execução Windows

Abra o PowerShell na raiz do projeto e permita a execução apenas para a sessão atual:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\windows_start_game.ps1
```

O script usa o launcher `py -3.11` quando disponível, cria `computer_vision\\.venv`, instala as dependências, inicia o servidor em `game_server` e executa `src\\reconhecimento_app.py`.

PowerShell é necessário porque o arquivo possui extensão `.ps1` e usa comandos próprios dessa linguagem.

## Menu principal

O arquivo `computer_vision/main.py` oferece:

1. Reconhecimento em tempo real
2. Treinamento
3. Captura de imagens para treinamento
4. Teste de câmera e MediaPipe
5. Saída

## Teste de instalação

Para testar a sintaxe e as dependências principais:

```bash
cd computer_vision
.venv/bin/python -m py_compile main.py config.py src/*.py src/sistema_libras/*.py
.venv/bin/python -c "import cv2, mediapipe, websockets; print('Dependências principais OK')"
```

Para testar câmera e MediaPipe pelo menu, execute `python main.py` e escolha a opção `4`.

## Câmeras

O sistema procura os índices de `0` a `9`. Depois da busca, ele mostra as câmeras encontradas e permite escolher uma delas. O índice mais comum é `0`.

Mensagens do OpenCV informando que índices inexistentes não puderam ser abertos são esperadas durante essa busca. Isso não significa necessariamente que a câmera válida esteja com problema.

## Captura de imagens

Crie uma pasta para cada classe dentro de:

```text
computer_vision/data/to_training/
```

Exemplo:

```text
computer_vision/data/to_training/
├── 1/
├── 2/
└── 3/
```

Execute `main.py`, escolha a opção `3` e selecione a câmera.

Durante a captura:

- `ESPAÇO`: salva uma imagem
- `ENTER`: avança para a próxima classe
- `R`: sincroniza o contador com as imagens existentes
- `Q`: encerra a captura

As imagens são salvas com nomes como:

```text
1_0001.jpg
1_0002.jpg
```

A interface desenhada na janela não é salva na imagem. O sistema evita sobrescrever imagens existentes e verifica se o arquivo foi salvo com sucesso.

## Treinamento

No menu, escolha `2. Treinamento`.

### Webcam

O sistema coleta características da mão diretamente da câmera. Para cada classe, pressione `ESPAÇO` quando a mão estiver detectada.

### Imagens em pastas

O sistema percorre as imagens de cada pasta, detecta a mão com MediaPipe e processa também a versão espelhada da imagem.

Cada mão gera 67 características:

```text
21 pontos x 3 coordenadas (x, y, z) = 63
4 ângulos dos dedos = 4
Total = 67 características
```

O classificador usado é um `SVC` com kernel `RBF`. Os dados são normalizados com `StandardScaler` e divididos em treinamento e teste.

A avaliação por imagens usa grupos para manter a imagem original e sua versão espelhada no mesmo conjunto, evitando uma precisão artificialmente alta.

São necessárias pelo menos duas classes e pelo menos duas amostras por classe.

## Modelo gerado

O modelo é salvo em:

```text
computer_vision/data/generated_model/modelo_libras.pkl
```

Esse arquivo contém:

- Classificador treinado
- Normalizador dos dados
- Mapeamento entre rótulos e números

O modelo só funciona corretamente com características extraídas pelo mesmo código e na mesma ordem.

## Reconhecimento em tempo real

Escolha `1. Reconhecimento em Tempo Real` no menu. O sistema:

1. Abre a câmera escolhida.
2. Detecta os pontos da mão.
3. Extrai as 67 características.
4. Normaliza os dados com o normalizador salvo.
5. Faz a previsão com o modelo.
6. Envia previsões de alta confiança pelo WebSocket quando disponível.

Pressione `Q` na janela da câmera para sair.

O reconhecimento atual é voltado principalmente para sinais estáticos. Ele não modela sequências temporais ou movimentos complexos ao longo de vários quadros.

## Servidor e WebSocket

O servidor Node.js fica em `game_server` e é iniciado com:

```bash
cd game_server
npm install
npm start
```

O reconhecimento tenta iniciar um servidor WebSocket local na porta `8765`. A interface do jogo pode consumir as previsões enviadas por esse canal.

## Problemas comuns

### Importação `cv2` não resolvida no VS Code

Selecione o interpretador correto:

```text
computer_vision/.venv/bin/python
```

No VS Code: `Ctrl+Shift+P` -> `Python: Select Interpreter`.

### `No module named websockets`

Use o ambiente do projeto:

```bash
cd computer_vision
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### `mediapipe has no attribute solutions`

O ambiente está usando uma versão incompatível. Instale:

```bash
python -m pip install --force-reinstall mediapipe==0.10.14
```

### Nenhuma classe encontrada

Verifique se existem subpastas dentro de:

```text
computer_vision/data/to_training/
```

### Modelo não encontrado

Treine o modelo antes de escolher o reconhecimento. O arquivo esperado é:

```text
computer_vision/data/generated_model/modelo_libras.pkl
```

### O script não encontra um arquivo

Execute os comandos a partir da raiz indicada no próprio comando. Para o menu Python:

```bash
cd computer_vision
python main.py
```

Os caminhos de dados são calculados a partir de `config.py`, portanto o sistema pode ser iniciado de outros diretórios quando o script correto é usado.

## Observações de qualidade dos dados

- Use iluminação uniforme.
- Mantenha a mão dentro do indicador central.
- Varie levemente posição, distância e orientação da mão.
- Colete quantidade semelhante de imagens para cada classe.
- Evite imagens sem mão detectada.
- Separe sinais visualmente muito parecidos com mais amostras.
- Teste o modelo com imagens e pessoas que não participaram da coleta.

## Limitações atuais

- O sistema reconhece características geométricas da mão, não a imagem completa.
- Sinais que dependem de movimento não são representados adequadamente.
- A qualidade depende da detecção do MediaPipe e da iluminação.
- O modelo é substituído quando um novo treinamento é salvo.
- Os scripts de inicialização devem ser executados no sistema operacional correspondente.
