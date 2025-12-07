import cv2
import numpy as np
from .utilitarios import UtilitariosMaos
from .classificador import ClassificadorLibras
import sys
import os
import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class ReconhecedorLibras:
    def __init__(self, indice_camera=0):
        self.utilitarios = UtilitariosMaos()
        self.classificador = ClassificadorLibras()
        self.historico = []
        self.ultima_previsao = "?"
        self.indice_camera = indice_camera
        
    def carregar_modelo(self, nome_arquivo="modelo_libras.pkl"):
        """Carrega modelo treinado"""
        return self.classificador.carregar_modelo(nome_arquivo)
    
    def executar_reconhecimento(self):
        """Executa reconhecimento em tempo real"""
        if not self.carregar_modelo():
            print("ERRO: Modelo não encontrado. Treine primeiro!")
            return
        
        camera = cv2.VideoCapture(self.indice_camera)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CONFIG['dimensao_imagem'][0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CONFIG['dimensao_imagem'][1])
        
        print("Reconhecimento iniciado. Pressione 'q' para sair.")
        
        while True:
            sucesso, quadro = camera.read()
            if not sucesso:
                continue
                
            quadro = cv2.flip(quadro, 1)
            quadro_rgb = cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)
            resultados = self.utilitarios.maos.process(quadro_rgb)
            
            previsao_atual = "?"
            confianca = 0.0
            # Determinar cor do indicador (padrão ciano)
            indicator_color = (255, 255, 0)

            if resultados.multi_hand_landmarks:
                altura, largura = quadro.shape[:2]
                tamanho_relativo = 0.25
                side = int(min(altura, largura) * tamanho_relativo)
                cx, cy = largura // 2, altura // 2
                half = side // 2
                tl_x, tl_y = cx - half, cy - half
                br_x, br_y = cx + half, cy + half

                for marcos_mao in resultados.multi_hand_landmarks:
                    # Desenhar landmarks
                    self.utilitarios.desenhar_landmarks(quadro, marcos_mao)

                    # Calcular bounding box da mão em pixels
                    xs = [lm.x for lm in marcos_mao.landmark]
                    ys = [lm.y for lm in marcos_mao.landmark]
                    min_x_px = int(min(xs) * largura)
                    max_x_px = int(max(xs) * largura)
                    min_y_px = int(min(ys) * altura)
                    max_y_px = int(max(ys) * altura)
                    center_x = (min_x_px + max_x_px) // 2
                    center_y = (min_y_px + max_y_px) // 2

                    # Verificar se o centro da mão está dentro do indicador
                    hand_in_indicator = (center_x >= tl_x and center_x <= br_x and
                                          center_y >= tl_y and center_y <= br_y)

                    # Fazer previsão apenas se a mão estiver dentro do indicador
                    if hand_in_indicator:
                        caracteristicas = self.utilitarios.extrair_caracteristicas(marcos_mao)
                        previsao_atual, confianca = self.classificador.prever(caracteristicas)
                        # Atualizar histórico
                        self._atualizar_historico(previsao_atual, confianca)

                        # Mudar cor do indicador: verde se classe reconhecida, azul se só mão detectada
                        if previsao_atual != "?":
                            indicator_color = (0, 255, 0)  # verde
                        else:
                            indicator_color = (255, 0, 0)  # azul

                        # Já encontramos uma mão relevante — não processar outras
                        break
            
            # Exibir resultados (passar cor do indicador)
            self._desenhar_interface(quadro, previsao_atual, confianca, indicator_color)
            
            cv2.imshow("Reconhecimento de Libras", quadro)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        camera.release()
        cv2.destroyAllWindows()
    
    def _atualizar_historico(self, previsao, confianca):
        """Atualiza histórico para suavizar previsões"""
        if previsao != "?":
            self.historico.append((previsao, confianca))
            # Manter apenas últimas 5 previsões
            if len(self.historico) > 5:
                self.historico.pop(0)
            
            # Usar moda do histórico para previsão final
            if len(self.historico) >= 3:
                previsoes = [p[0] for p in self.historico]
                previsao_final = max(set(previsoes), key=previsoes.count)
                self.ultima_previsao = previsao_final
    
    def _desenhar_interface(self, quadro, previsao, confianca, indicator_color=None):
        """Desenha interface na tela - SEMPRE mostra resultado"""

        altura, largura = quadro.shape[:2]
        
        # Indicador central (onde posicionar a mão para reconhecimento)
        # Quadrado de tamanho relativo à menor dimensão do frame
        tamanho_relativo = 0.25
        side = int(min(altura, largura) * tamanho_relativo)
        cx, cy = largura // 2, altura // 2
        half = side // 2
        tl = (cx - half, cy - half)
        br = (cx + half, cy + half)
        cor_indicador = indicator_color if indicator_color is not None else (255, 255, 0)  # ciano BGR
        espessura = 1
        cv2.rectangle(quadro, tl, br, cor_indicador, espessura, lineType=cv2.LINE_AA)

        # Calcular tamanho do painel (1/4 da largura)
        largura_painel = 250
        altura_painel = 140

        # Fundo semi-transparente para o painel
        # OBS: a lógica abaixo escurece toda a imagem porque faz blend
        # entre a imagem original e a cópia (overlay). Isso deixa o
        # quadro mais escuro globalmente. Comentado para preservar
        # brilho da imagem inteira (painel ainda será desenhado em cima).
        overlay = quadro.copy()
        cv2.rectangle(overlay, (0, 0), (largura_painel, altura_painel), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, quadro, 0.7, 0, quadro)
        
        # Borda do painel
        cv2.rectangle(quadro, (0, 0), (largura_painel, altura_painel), (0, 255, 0), 2)

        # Definir cores baseadas na confiança
        if confianca > 0.8:
            cor_texto = (0, 255, 0)  # Verde - Muito confiável
            status = "ALTA CONFIANCA"
        elif confianca > 0.6:
            cor_texto = (0, 255, 255)  # Amarelo - Confiável
            status = "CONFIANCA MEDIA"
        elif confianca > 0.4:
            cor_texto = (0, 165, 255)  # Laranja - Pouco confiável  
            status = "BAIXA CONFIANCA"
        else:
            cor_texto = (0, 0, 255)  # Vermelho - Muito baixa
            status = "MUITO BAIXA CONFIANCA"
        
        # Sempre mostrar a previsão, mesmo com confiança baixa
        cv2.putText(quadro, f"SINAL: {previsao}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_texto, 3)
        
        # Mostrar confiança com barra visual
        cv2.putText(quadro, f"CONFIANCA: {confianca:.3f}", (20, 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_texto, 2)
        
        # Barra de confiança visual
        largura_barra = 200
        altura_barra = 20
        x_barra = 20
        y_barra = 100
        
        # Fundo da barra (cinza)
        cv2.rectangle(quadro, (x_barra, y_barra), 
                    (x_barra + largura_barra, y_barra + altura_barra), 
                    (100, 100, 100), -1)
        
        # Preenchimento da barra (baseado na confiança)
        comprimento_preenchimento = int(confianca * largura_barra)
        cv2.rectangle(quadro, (x_barra, y_barra), 
                    (x_barra + comprimento_preenchimento, y_barra + altura_barra), 
                    cor_texto, -1)
        
        # Borda da barra
        cv2.rectangle(quadro, (x_barra, y_barra), 
                    (x_barra + largura_barra, y_barra + altura_barra), 
                    (255, 255, 255), 1)
        
        # Status textual
        cv2.putText(quadro, f"STATUS: {status}", (20, 135), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, cor_texto, 1)
        
        # Mostrar todas as probabilidades (opcional - para debug)
        if hasattr(self, 'mostrar_detalhes') and self.mostrar_detalhes:
            self._mostrar_probabilidades_detalhadas(quadro, confianca)
        
        # Previsão suavizada do histórico
        # if self.ultima_previsao != "?":
        #     cv2.putText(quadro, f"SUAVIZADO: {self.ultima_previsao}", (20, 450), 
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Instruções
        cv2.putText(quadro, "Pressione 'q' para sair", (400, 470), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def _mostrar_probabilidades_detalhadas(self, quadro, confianca_atual):
        """Mostra as top 3 previsões (opcional)"""
        try:
            # Esta função precisa acessar as probabilidades diretamente
            # Você pode adicionar isso no método prever() se quiser
            pass
        except:
            pass