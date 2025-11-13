import cv2
import numpy as np
from .utilitarios import UtilitariosMaos
from .classificador import ClassificadorLibras
import config

class ReconhecedorLibras:
    def __init__(self):
        self.utilitarios = UtilitariosMaos()
        self.classificador = ClassificadorLibras()
        self.historico = []
        self.ultima_previsao = "?"
        
    def carregar_modelo(self, nome_arquivo="modelo_libras.pkl"):
        """Carrega modelo treinado"""
        return self.classificador.carregar_modelo(nome_arquivo)
    
    def executar_reconhecimento(self):
        """Executa reconhecimento em tempo real"""
        if not self.carregar_modelo():
            print("ERRO: Modelo não encontrado. Treine primeiro!")
            return
        
        camera = cv2.VideoCapture(0)
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
            
            if resultados.multi_hand_landmarks:
                for marcos_mao in resultados.multi_hand_landmarks:
                    # Desenhar landmarks
                    self.utilitarios.desenhar_landmarks(quadro, marcos_mao)
                    
                    # Fazer previsão
                    caracteristicas = self.utilitarios.extrair_caracteristicas(marcos_mao)
                    previsao_atual, confianca = self.classificador.prever(caracteristicas)
                    
                    # Atualizar histórico
                    self._atualizar_historico(previsao_atual, confianca)
            
            # Exibir resultados
            self._desenhar_interface(quadro, previsao_atual, confianca)
            
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
    
    def _desenhar_interface1(self, quadro, previsao, confianca):
        """Desenha interface na tela"""
        # Fundo para texto
        cv2.rectangle(quadro, (0, 0), (400, 120), (0, 0, 0), -1)
        
        # Previsão atual
        cor_texto = (0, 255, 0) if confianca > config.CONFIG['limite_confianca'] else (0, 0, 255)
        cv2.putText(quadro, f"SINAL: {previsao}", (20, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, cor_texto, 2)
        cv2.putText(quadro, f"CONFIANCA: {confianca:.2f}", (20, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_texto, 2)
        
        # Previsão suavizada do histórico
        if self.ultima_previsao != "?":
            cv2.putText(quadro, f"SUAVIZADO: {self.ultima_previsao}", (20, 450), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Instruções
        cv2.putText(quadro, "Pressione 'q' para sair", (400, 470), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
    def _desenhar_interface(self, quadro, previsao, confianca):
        """Desenha interface na tela - SEMPRE mostra resultado"""
        # Fundo para texto
        cv2.rectangle(quadro, (0, 0), (500, 140), (0, 0, 0), -1)
        
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
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, cor_texto, 3)
        
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
        cv2.putText(quadro, f"STATUS: {status}", (20, 130), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor_texto, 1)
        
        # Mostrar todas as probabilidades (opcional - para debug)
        if hasattr(self, 'mostrar_detalhes') and self.mostrar_detalhes:
            self._mostrar_probabilidades_detalhadas(quadro, confianca)
        
        # Previsão suavizada do histórico
        if self.ultima_previsao != "?":
            cv2.putText(quadro, f"SUAVIZADO: {self.ultima_previsao}", (20, 450), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
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