# Sistema de Reconhecimento de LibrasNaval

Sistema para treinamento e reconhecimento de sinais de LIBRAS em tempo real, integrado a interface do jogo por WebSocket.

## Requisitos

- Python 3.11
- Node.js e npm
- Camera compativel com OpenCV
- Ambiente grafico para as janelas da camera

O detector usa MediaPipe Tasks e o treinamento usa scikit-learn.

## Instalacao e execucao Linux

Na primeira execução, instale o ambiente e as dependências:

```bash
./install.sh
```

O instalador prepara um ambiente virtual Python em `detection_system/.venv`,
instala as dependências Python e Node.js e, quando necessário, os pré-requisitos
do sistema. O preparo automático é voltado a Ubuntu e Debian; requer internet e
`sudo` (não execute o instalador inteiro como root). Se Python 3.11 não estiver
disponível como pacote, o instalador compila a versão estável mais recente da
série 3.11. Se Node.js 18 ou superior não estiver disponível, configura o
repositório NodeSource e instala Node.js 22.

Depois, inicie o jogo:

```bash
./start.sh
```

`start.sh` não instala dependências: ele inicia o servidor HTTP na porta 3000 e
exibe um menu para abrir a página web no navegador ou executar o menu Python
com o ambiente virtual existente. A página também pode ser acessada
manualmente em <http://localhost:3000>.

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

No menu de treinamento, a opção **Ver estatísticas dos sinais** lista as
classes gravadas, o modo e as sessões registradas. A opção **Excluir um sinal
gravado** remove todas as amostras de uma classe após confirmação explícita e
retreina o modelo com os dados restantes. Se os dados não forem suficientes
para gerar um modelo válido, o modelo correspondente é removido até que novas
classes sejam treinadas.

## Reconhecimento hibrido

Durante o jogo, o sistema analisa os dois tipos sem pedir uma selecao previa:

```text
camera -> MediaPipe -> landmarks -> modelos estatico e dinamico -> WebSocket -> jogo
```

Uma mao estavel favorece o modelo estatico; um movimento detectado favorece o modelo dinamico. Os limites podem ser ajustados em [detection_system/config.py](detection_system/config.py).

## Dados de partidas

Ao concluir uma partida, o navegador salva um registro local em
`localStorage` com a faixa etária selecionada, identificador de sessão, data,
duração, jogadas, acertos, erros, precisão e a quantidade de jogadas feitas
por Libras e por mouse. O histórico usa a chave `librasNaval.resultados` e
permite comparar, futuramente, o desempenho por faixa etária e por modalidade
de interação. Os dados não são enviados a um servidor.

Os relatórios podem ser visualizados no mesmo navegador em
<http://localhost:3000/relatorios.html>. Essa página não é vinculada às telas
do jogo e permite exportar o histórico em CSV ou JSON.

Durante o desenvolvimento, o botão **Limpar registros** da página de
relatórios remove o histórico de partidas do navegador após confirmação. Essa
ação não remove os modelos nem os dados de treinamento do sistema Python.

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
