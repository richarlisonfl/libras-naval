import cv2
import os
import numpy as np
from .utilitarios import UtilitariosMaos
import config

class ColetorDadosLibras:
    def __init__(self, indice_camera=0):
        self.utilitarios = UtilitariosMaos()
        self.dados = []
        self.rotulos = []
        self.classe_atual = "A"
        self.contador_amostras = 0
        self.indice_camera = indice_camera
        
        # Criar diretório se não existir
        os.makedirs(config.CONFIG['caminho_dados'], exist_ok=True)
    
    def coletar_classe(self, classe):
        """Coleta amostras para uma classe específica (letra ou número)"""
        self.classe_atual = classe
        self.contador_amostras = 0
        
        print(f"\n=== COLETANDO DADOS PARA: {classe} ===")
        print("Posicione sua mão e pressione ESPAÇO para capturar")
        print("Pressione 'q' para terminar ou 's' para pular")
        
        camera = cv2.VideoCapture(self.indice_camera)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CONFIG['dimensao_imagem'][0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CONFIG['dimensao_imagem'][1])
        
        while self.contador_amostras < config.CONFIG['numero_amostras_por_classe']:
            sucesso, quadro = camera.read()
            if not sucesso:
                continue
                
            quadro = cv2.flip(quadro, 1)
            quadro_rgb = cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)
            resultados = self.utilitarios.maos.process(quadro_rgb)
            
            # Interface de coleta
            cv2.putText(quadro, f"CLASSE: {classe}", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(quadro, f"AMOSTRAS: {self.contador_amostras}/{config.CONFIG['numero_amostras_por_classe']}", 
                       (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(quadro, "ESPACO: Capturar | 's': Pular | 'q': Sair", 
                       (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            mao_detectada = False
            if resultados.multi_hand_landmarks:
                mao_detectada = True
                for marcos_mao in resultados.multi_hand_landmarks:
                    self.utilitarios.desenhar_landmarks(quadro, marcos_mao)
            
            # Feedback visual
            cor_feedback = (0, 255, 0) if mao_detectada else (0, 0, 255)
            texto_feedback = "MAO DETECTADA - PRONTO" if mao_detectada else "AGUARDANDO MAO"
            cv2.putText(quadro, texto_feedback, (20, 450), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor_feedback, 2)
            
            cv2.imshow("Coletor de Dados - Libras", quadro)
            
            tecla = cv2.waitKey(1) & 0xFF
            if tecla == ord(' ') and mao_detectada:  # Espaço para capturar
                self._salvar_amostra(resultados.multi_hand_landmarks[0], classe)
            elif tecla == ord('s'):  # Pular esta classe
                break
            elif tecla == ord('q'):  # Sair completamente
                camera.release()
                cv2.destroyAllWindows()
                return False
        
        camera.release()
        cv2.destroyAllWindows()
        return True
    
    def _salvar_amostra(self, marcos_mao, classe):
        """Salva uma amostra individual"""
        caracteristicas = self.utilitarios.extrair_caracteristicas(marcos_mao)
        self.dados.append(caracteristicas)
        self.rotulos.append(classe)
        self.contador_amostras += 1
        print(f"Amostra {self.contador_amostras} salva para {classe}")
    
    def salvar_dados(self, nome_arquivo="dados_libras.npz"):
        """Salva todos os dados coletados"""
        caminho = os.path.join(config.CONFIG['caminho_dados'], nome_arquivo)
        np.savez(caminho, dados=self.dados, rotulos=self.rotulos)
        print(f"Dados salvos em: {caminho}")
    
    def carregar_dados(self, nome_arquivo="dados_libras.npz"):
        """Carrega dados salvos"""
        caminho = os.path.join(config.CONFIG['caminho_dados'], nome_arquivo)
        if os.path.exists(caminho):
            dados = np.load(caminho)
            self.dados = dados['dados'].tolist()
            self.rotulos = dados['rotulos'].tolist()
            print(f"Dados carregados: {len(self.dados)} amostras")
            return True
        return False