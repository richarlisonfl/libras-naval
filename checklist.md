# Checklist de treinamento do LibrasNaval

## 1. Ambiente

- [ ] Python 3.11 e a virtualenv `detection_system/.venv` estão funcionando.
- [ ] `python -m pip check` não mostra conflitos.
- [ ] A câmera abre e entrega frames sem travar.
- [ ] O MediaPipe `1.0.1` inicializa com o modelo `hand_landmarker.task`.
- [ ] A janela mostra os landmarks, lado da mão e orientação corretamente.
- [ ] O teste é encerrado somente com `q`.

## 2. Preparação da coleta

- [ ] O sinal foi escolhido individualmente, por exemplo `A`, `B` ou `J`.
- [ ] O identificador da pessoa foi informado de forma consistente.
- [ ] O fundo tem contraste com a mão.
- [ ] A iluminação vem principalmente da frente ou dos lados.
- [ ] A mão inteira permanece visível, sem cortes nas pontas dos dedos.
- [ ] A câmera fica parada e na altura das mãos.
- [ ] Foram coletadas mão esquerda e mão direita quando o sinal permitir.

## 3. Sinais estáticos

- [ ] Foram coletadas pelo menos 100 amostras por sinal e por pessoa.
- [ ] O mínimo aceitável para um protótipo é 50 amostras por sinal e por pessoa.
- [ ] A meta recomendada é 3 a 5 pessoas, totalizando 300 a 500 amostras por sinal.
- [ ] As amostras variam levemente em posição, distância, rotação e iluminação.
- [ ] Cada sinal possui pelo menos duas pessoas diferentes antes da avaliação final.
- [ ] O sinal foi treinado usando a opção de sinal estático individual.
- [ ] `modelo_libras.pkl` e `dados_libras.npz` foram gerados.

## 4. Sinais dinâmicos

- [ ] Foram coletadas sequências completas, do início ao fim do movimento.
- [ ] Cada sequência possui aproximadamente 30 a 60 frames válidos.
- [ ] Para um sinal como `J`, foram usadas pelo menos 30 sequências por pessoa.
- [ ] A meta recomendada é 3 a 5 pessoas e 100 a 200 sequências por sinal.
- [ ] A velocidade do movimento varia entre as sequências.
- [ ] Foram coletadas variações de amplitude, posição e orientação da mão.
- [ ] O sinal `J` foi coletado com o movimento completo, sem interromper no meio.
- [ ] Cada sinal dinâmico foi treinado individualmente.
- [ ] `modelo_dinamico.pkl` e `sequencias_libras.npz` foram gerados.

## 5. Treinamento incremental

- [ ] O sinal novo não substituiu os dados antigos.
- [ ] O sistema carregou as características ou sequências anteriores.
- [ ] O catálogo registrou a pessoa e incrementou as sessões do sinal.
- [ ] O modelo foi retreinado com dados antigos e novos juntos.
- [ ] Para reforçar um sinal, foi coletada uma nova sessão apenas dele.
- [ ] Sinais com baixa confiança receberam novas amostras antes dos demais.
- [ ] Não é necessário manter as imagens depois que as características forem salvas.
- [ ] Os arquivos de características não foram apagados antes do retreinamento.

## 6. Avaliação

- [ ] As pessoas usadas no teste não participaram da coleta de treinamento.
- [ ] Cada sinal foi testado pelo menos 20 vezes.
- [ ] Foram registradas previsões corretas, incorretas e `?`.
- [ ] A confiança média foi observada por sinal, não apenas no conjunto total.
- [ ] Sinais parecidos foram avaliados lado a lado.
- [ ] Palma, costas e lateral foram testadas quando fizerem parte do sinal.
- [ ] O modelo não depende de uma única pessoa, distância ou iluminação.
- [ ] O modelo está versionado junto com `requirements.txt`.

## Quantidades recomendadas

| Tipo | Mínimo de protótipo | Recomendado |
|---|---:|---:|
| Estático, por pessoa e sinal | 50 imagens | 100 imagens |
| Pessoas por sinal | 2 | 3 a 5 |
| Dinâmico, por pessoa e sinal | 15 sequências | 30 a 50 sequências |
| Frames por sequência dinâmica | 20 | 30 a 60 |
| Testes independentes por sinal | 10 | 20 ou mais |

O contador mantido em `catalogo_treinamento.json` representa pessoas distintas e
sessões de coleta por sinal. Ele não substitui uma métrica de qualidade: um sinal
pode ter muitas sessões e ainda precisar de novas amostras se sua confiança for
baixa ou se falhar com pessoas não usadas no treinamento.

## Comandos úteis

```bash
cd detection_system
source .venv/bin/activate
python main.py
```

Fluxo recomendado no menu:

1. `2. Treinamento`
2. `1. Treinar um sinal estático` ou `2. Treinar um sinal com movimento`
3. Informe um sinal por vez.
4. Repita a coleta somente para sinais com baixa qualidade.
5. Use `1. Reconhecimento em Tempo Real` e escolha o modo estático ou dinâmico.
