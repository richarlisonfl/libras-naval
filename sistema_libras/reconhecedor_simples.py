import cv2
import numpy as np
from .utilitarios import UtilitariosMaos
from .classificador import ClassificadorLibras
import config

class ReconhecedorLibrasSimples:
    def __init__(self):
        self.utilitarios = UtilitariosMaos()
        self.classificador = ClassificadorLibras()
        self.historico = []
        
    def carregar_modelo(self, nome_arquivo="modelo_libras.pkl"):
        return self.classificador.carregar_modelo(nome_arquivo)
    
    def executar_reconhecimento(self):
        """Versão simples que sempre mostra resultados"""
        if not self.carregar_modelo():
            print("❌ Modelo não encontrado!")
            return
        
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CONFIG['dimensao_imagem'][0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CONFIG['dimensao_imagem'][1])
        
        print("🔍 Reconhecimento iniciado - Sempre mostra resultados!")
        
        while True:
            sucesso, quadro = camera.read()
            if not sucesso:
                continue
                
            quadro = cv2.flip(quadro, 1)
            resultados = self.utilitarios.maos.process(cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB))
            
            previsao = "?"
            confianca = 0.0
            
            if resultados.multi_hand_landmarks:
                for marcos_mao in resultados.multi_hand_landmarks:
                    self.utilitarios.desenhar_landmarks(quadro, marcos_mao)
                    
                    caracteristicas = self.utilitarios.extrair_caracteristicas(marcos_mao)
                    previsao, confianca = self.classificador.prever(caracteristicas)
            
            # SEMPRE mostrar resultado, independente da confiança
            self._desenhar_resultado_simples(quadro, previsao, confianca)
            
            cv2.imshow("Libras - Sempre Mostra Resultado", quadro)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        camera.release()
        cv2.destroyAllWindows()
    
    def _desenhar_resultado_simples(self, quadro, previsao, confianca):
        """Interface simples que sempre mostra o resultado"""
        # Cor baseada na confiança
        if confianca > 0.7:
            cor = (0, 255, 0)  # Verde
        elif confianca > 0.4:
            cor = (0, 255, 255)  # Amarelo
        else:
            cor = (0, 0, 255)  # Vermelho
        
        # Sempre mostrar a previsão
        texto_principal = f"SINAL: {previsao}"
        cv2.putText(quadro, texto_principal, (20, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, cor, 3)
        
        # Mostrar confiança como porcentagem
        texto_confianca = f"Confianca: {confianca*100:.1f}%"
        cv2.putText(quadro, texto_confianca, (20, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)
        
        # Legenda de cores
        if confianca <= 0.4:
            cv2.putText(quadro, "BAIXA CONFIANCA", (20, 450), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)