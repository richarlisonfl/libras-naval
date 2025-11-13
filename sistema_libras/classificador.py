import numpy as np
import pickle
import os
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import config

class ClassificadorLibras:
    def __init__(self):
        self.modelo = None
        self.scaler = StandardScaler()
        self.encoder_rotulos = {}
        self.decoder_rotulos = {}
    
    def preparar_dados(self, dados, rotulos):
        """Prepara dados para treinamento"""
        # Converter rótulos para números
        rotulos_unicos = list(set(rotulos))
        self.encoder_rotulos = {rotulo: idx for idx, rotulo in enumerate(rotulos_unicos)}
        self.decoder_rotulos = {idx: rotulo for rotulo, idx in self.encoder_rotulos.items()}
        
        rotulos_numericos = [self.encoder_rotulos[r] for r in rotulos]
        
        # Normalizar dados
        dados_array = np.array(dados)
        dados_normalizados = self.scaler.fit_transform(dados_array)
        
        return dados_normalizados, np.array(rotulos_numericos)
    
    def treinar(self, dados, rotulos, test_size=0.2):
        """Treina o modelo de classificação"""
        X, y = self.preparar_dados(dados, rotulos)
        
        # Dividir em treino e teste
        X_treino, X_teste, y_treino, y_teste = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Criar e treinar modelo
        self.modelo = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True)
        self.modelo.fit(X_treino, y_treino)
        
        # Avaliar
        precisao_treino = self.modelo.score(X_treino, y_treino)
        precisao_teste = self.modelo.score(X_teste, y_teste)
        
        print(f"Precisão Treino: {precisao_treino:.3f}")
        print(f"Precisão Teste: {precisao_teste:.3f}")
        
        return precisao_teste
    
    def prever(self, caracteristicas):
        """Faz previsão para novas características"""
        if self.modelo is None:
            return "Modelo não treinado", 0.0
        
        # Normalizar características
        carac_normalizadas = self.scaler.transform([caracteristicas])
        
        # Fazer previsão
        probabilidades = self.modelo.predict_proba(carac_normalizadas)[0]
        indice_previsto = np.argmax(probabilidades)
        confianca = probabilidades[indice_previsto]

        # SEMPRE retornar resultado, independente da confiança
        # letra_prevista = self.decoder_rotulos[indice_previsto]
        # return letra_prevista, confianca 
        
        if confianca > config.CONFIG['limite_confianca']:
            return self.decoder_rotulos[indice_previsto], confianca
        else:
            return "?", confianca
         
    
    def salvar_modelo(self, nome_arquivo="modelo_libras.pkl"):
        """Salva o modelo treinado"""
        os.makedirs(config.CONFIG['caminho_modelos'], exist_ok=True)
        caminho = os.path.join(config.CONFIG['caminho_modelos'], nome_arquivo)
        
        with open(caminho, 'wb') as f:
            pickle.dump({
                'modelo': self.modelo,
                'scaler': self.scaler,
                'encoder': self.encoder_rotulos,
                'decoder': self.decoder_rotulos
            }, f)
        print(f"Modelo salvo em: {caminho}")
    
    def carregar_modelo(self, nome_arquivo="modelo_libras.pkl"):
        """Carrega modelo salvo"""
        caminho = os.path.join(config.CONFIG['caminho_modelos'], nome_arquivo)
        
        if os.path.exists(caminho):
            with open(caminho, 'rb') as f:
                dados = pickle.load(f)
                self.modelo = dados['modelo']
                self.scaler = dados['scaler']
                self.encoder_rotulos = dados['encoder']
                self.decoder_rotulos = dados['decoder']
            print(f"Modelo carregado: {len(self.decoder_rotulos)} classes")
            return True
        return False