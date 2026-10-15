# LibrasNaval: jogo educativo com reconhecimento de sinais em Libras

## Introdução

A Federação Nacional de Educação e Integração dos Surdos (FENEIS) afirma que a Língua Brasileira de Sinais (Libras) pode ser aprendida por qualquer pessoa interessada em se comunicar com a comunidade surda. Como qualquer idioma, a Libras possui características próprias que trazem facilidades e desafios durante o processo de aprendizagem.

O presente projeto apresenta uma dualidade de objetivos, articulando a promoção da inclusão social por meio da gamificação com o incentivo ao estudo e à aplicação de tecnologias emergentes. Nesse contexto, busca-se utilizar a Libras como elemento de aproximação entre a acessibilidade comunicacional e a inovação tecnológica, desenvolvendo uma ferramenta lúdica que estimule pessoas não surdas a conhecerem e aprenderem a língua utilizada pela comunidade surda.

Para alcançar esse propósito, foi desenvolvido o LibrasNaval, um jogo que integra conceitos de Aprendizado de Máquina (*Machine Learning*) e Visão Computacional (*Computer Vision*), permitindo que sinais realizados por pessoas sejam capturados e classificados pelo sistema. Dessa forma, a interação com o jogo pode se tornar uma oportunidade de aprendizagem tanto para o jogador, incentivado a reconhecer e reproduzir sinais, quanto para o desenvolvimento do sistema computacional, cujo modelo é treinado para identificar padrões visuais associados às classes de sinais utilizadas no projeto.

Além de sua finalidade inclusiva e educacional, o projeto busca despertar o interesse dos estudantes do Instituto Federal do Pará (IFPA) pelas tecnologias que fundamentam os avanços contemporâneos da Inteligência Artificial, incluindo aprendizado de máquina, redes neurais artificiais, mineração de dados (*Data Mining*) e modelos de linguagem de grande escala (*Large Language Models* — LLMs). Assim, o LibrasNaval propõe uma abordagem interdisciplinar na qual o desenvolvimento de um jogo educativo constitui, simultaneamente, um instrumento de sensibilização para a inclusão e uma aplicação prática de conceitos de computação inteligente.

## Desenvolvimento do jogo

Para atender aos objetivos propostos pelo projeto, foi implementado o jogo Batalha Naval com os conhecimentos adquiridos em sala de aula e utilizando HTML, CSS, JavaScript e Bootstrap. O tabuleiro possui dimensões de 5 × 5: as cinco colunas são identificadas pelas vogais A, E, I, O e U, e as cinco linhas são numeradas de 1 a 5, conforme ilustrado na Figura 1. Essa organização foi escolhida porque os sinais correspondentes podem ser reproduzidos com apenas uma mão. No início de cada partida, os navios são dispostos aleatoriamente no tabuleiro.

Para realizar uma jogada, o jogador produz os sinais correspondentes à coordenada desejada. Por exemplo, para selecionar a coluna A e a linha 3, realiza os sinais da letra A e do número 3, além do gesto de confirmação utilizado pelo sistema. O sistema captura e interpreta os sinais e, quando a classificação é considerada confiável, envia os comandos à interface do jogo para registrar o tiro no tabuleiro.

## Captura e reconhecimento de sinais

O LibrasNaval combina técnicas de visão computacional e aprendizado de máquina para identificar sinais realizados diante da câmera e utilizá-los como comandos no jogo. O processo envolve a captura de imagens, a localização de pontos de referência da mão, a extração de características e a classificação do sinal. A comunicação entre o módulo de reconhecimento e a interface do jogo é realizada por meio de uma conexão WebSocket local.

### Captura e detecção da mão

No fluxo principal do jogo, a câmera é acessada pelo módulo de reconhecimento em Python, com auxílio da biblioteca OpenCV. Os quadros de vídeo são capturados continuamente, espelhados para facilitar a interação do jogador e convertidos do formato de cores BGR para RGB, exigido pelo MediaPipe. A configuração do sistema prevê imagens de 640 × 480 pixels e processamento a 30 quadros por segundo.

Em seguida, o MediaPipe Hand Landmarker identifica os pontos de referência (*landmarks*) da mão. O modelo pode detectar até duas mãos e, para cada uma, estima 21 pontos tridimensionais correspondentes a regiões como o pulso e as articulações dos dedos. Na etapa de classificação do LibrasNaval, as características são extraídas da primeira mão detectada no quadro. Os pontos identificados também podem ser desenhados sobre a imagem, auxiliando a visualização durante o reconhecimento e o treinamento.

### Extração de características

Em vez de utilizar diretamente os pixels da imagem como entrada dos classificadores desenvolvidos para o projeto, o sistema representa a mão por um conjunto de características numéricas. Para cada quadro, são utilizadas 68 características: as coordenadas x, y e z dos 21 pontos de referência, que totalizam 63 valores; quatro ângulos associados às articulações dos dedos; e uma medida relacionada à orientação da mão em relação à câmera.

Essa representação reduz a entrada a aspectos geométricos da configuração da mão. Durante o treinamento e a inferência, os dados são normalizados pelo `StandardScaler`, etapa que ajusta as escalas das características antes de sua utilização pelos classificadores.

### Treinamento dos modelos

O sistema contempla sinais estáticos e dinâmicos. No treinamento estático, cada captura fornece uma amostra que representa uma configuração da mão. No treinamento dinâmico, são coletados vários quadros ao longo da execução do sinal, formando uma sequência que preserva informações sobre o movimento.

As amostras de treinamento são obtidas diretamente da câmera e convertidas em características numéricas; as imagens originais não são armazenadas pelo fluxo de treinamento descrito no projeto. Os dados numéricos, os rótulos e os modelos treinados são salvos localmente para que possam ser carregados em sessões posteriores. A quantidade mínima necessária para treinar depende do tipo de sinal: o treinamento exige pelo menos duas classes, e cada classe estática precisa conter ao menos duas amostras.

Para a classificação dos sinais estáticos, o projeto utiliza uma Máquina de Vetores de Suporte (*Support Vector Classifier* — SVC) com função de base radial (RBF), implementada com a biblioteca scikit-learn. Os rótulos das amostras são codificados numericamente durante o treinamento e associados novamente às classes textuais na etapa de previsão.

No caso dos sinais dinâmicos, a sequência de quadros é resumida em características temporais: os valores do primeiro e do último quadro, além de estatísticas das variações entre quadros — média, desvio-padrão e maior variação absoluta. O resumo resultante é normalizado e classificado por outro SVC. Durante o reconhecimento, o sistema mantém uma janela de até 45 quadros para avaliar a sequência.

### Classificação em tempo real

Durante o reconhecimento, as características extraídas de cada quadro são avaliadas pelos modelos disponíveis. A decisão entre as abordagens estática e dinâmica considera a variação dos pontos de referência entre quadros. Quando o movimento ultrapassa o limiar configurado, o sistema prioriza a previsão dinâmica caso ela atinja o nível mínimo de confiança definido. Caso contrário, pode utilizar a previsão estática disponível.

O classificador estima probabilidades para as classes treinadas. O sistema utiliza limiares de confiança para decidir se aceita uma classificação ou a trata como inconclusiva. Para evitar o envio repetido de um mesmo resultado a cada quadro, há também um intervalo mínimo entre mensagens idênticas enviadas ao jogo. A eficácia do reconhecimento depende, entre outros fatores, da qualidade das amostras de treinamento e das condições de captura, como iluminação, enquadramento e posicionamento da mão.

É importante destacar que o modelo classifica as categorias para as quais foi treinado; ele não reconhece automaticamente todos os sinais da Libras. O treinamento realizado no projeto é baseado em amostras rotuladas, coletadas previamente por meio da câmera, e não corresponde a um processo de aprendizagem contínua durante cada partida.

### Gesto de início e comunicação com a interface

O gesto utilizado para iniciar a interação tem um tratamento distinto do reconhecimento dos sinais treinados para o jogo. O projeto utiliza o Gesture Recognizer do MediaPipe para detectar o gesto *I Love You* (ILY). Quando a confiança estimada atinge o limiar configurado, o módulo Python envia a mensagem de início ao navegador.

Para os sinais reconhecidos durante a partida, o módulo envia os rótulos por WebSocket. A interface do jogo recebe essas mensagens e as interpreta como comandos para selecionar uma vogal, indicar uma linha ou confirmar uma ação. No código atual, a confirmação de jogada é associada à mensagem `ok`, enquanto o gesto ILY é utilizado para iniciar a interação. Portanto, se a versão do jogo descrita no artigo deve utilizar ILY para confirmar cada coordenada, essa regra precisa ser implementada no código antes de se afirmar que esse é o comportamento atual.

Em síntese, o fluxo de reconhecimento pode ser representado da seguinte forma:

> **Câmera → OpenCV → MediaPipe → landmarks da mão → extração de características → classificação estática ou dinâmica → WebSocket → interface do jogo**

## Considerações finais

A arquitetura do LibrasNaval integra captura de vídeo, detecção de pontos da mão, extração de características, classificação por aprendizado de máquina e comunicação com uma aplicação web. Essa integração permite que sinais configurados e treinados para o projeto sejam utilizados como comandos em uma atividade lúdica. Além de apoiar a proposta educacional e inclusiva, o sistema oferece um contexto prático para explorar conceitos de visão computacional e aprendizado de máquina.
