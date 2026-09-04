import json
import os
import pickle

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

import config


class ClassificadorTemporal:
    """Classifica sequências de características de sinais com movimento."""

    MODELO = "modelo_dinamico.pkl"
    DADOS = "sequencias_libras.npz"
    CATALOGO = "catalogo_treinamento.json"

    def __init__(self):
        self.modelo = None
        self.scaler = StandardScaler()
        self.decoder_rotulos = {}

    @staticmethod
    def resumir_sequencia(sequencia):
        """Transforma uma sequência em características temporais fixas."""
        sequencia = np.asarray(sequencia, dtype=float)
        if sequencia.ndim != 2 or len(sequencia) < 2:
            raise ValueError("Uma sequência precisa ter ao menos dois frames.")
        velocidade = np.diff(sequencia, axis=0)
        return np.concatenate((
            sequencia[0],
            sequencia[-1],
            np.mean(velocidade, axis=0),
            np.std(velocidade, axis=0),
            np.max(np.abs(velocidade), axis=0),
        ))

    def treinar(self, sequencias, rotulos):
        if len(sequencias) != len(rotulos):
            raise ValueError("A quantidade de sequências e rótulos deve ser igual.")
        if len(set(rotulos)) < 2:
            raise ValueError("São necessárias pelo menos duas classes dinâmicas.")
        amostras = {rotulo: rotulos.count(rotulo) for rotulo in set(rotulos)}
        if min(amostras.values()) < 2:
            raise ValueError("Cada sinal dinâmico precisa de pelo menos duas sequências.")

        dados = np.array([self.resumir_sequencia(seq) for seq in sequencias])
        classes = sorted(set(rotulos))
        encoder = {classe: indice for indice, classe in enumerate(classes)}
        self.decoder_rotulos = {indice: classe for classe, indice in encoder.items()}
        rotulos_numericos = np.array([encoder[rotulo] for rotulo in rotulos])
        dados = self.scaler.fit_transform(dados)
        treino, teste, y_treino, y_teste = train_test_split(
            dados, rotulos_numericos, test_size=0.2, random_state=42,
            stratify=rotulos_numericos,
        )
        self.modelo = SVC(kernel="rbf", probability=True, random_state=42)
        self.modelo.fit(treino, y_treino)
        return self.modelo.score(teste, y_teste)

    def prever(self, sequencia):
        if self.modelo is None:
            return "?", 0.0
        caracteristicas = self.scaler.transform([self.resumir_sequencia(sequencia)])
        probabilidades = self.modelo.predict_proba(caracteristicas)[0]
        indice = int(np.argmax(probabilidades))
        return self.decoder_rotulos[indice], float(probabilidades[indice])

    def salvar(self, sequencias, rotulos):
        caminho = config.CONFIG["caminho_modelos"]
        os.makedirs(caminho, exist_ok=True)
        np.savez_compressed(
            os.path.join(caminho, self.DADOS),
            sequencias=np.asarray(sequencias, dtype=float),
            rotulos=np.asarray(rotulos),
        )
        with open(os.path.join(caminho, self.MODELO), "wb") as arquivo:
            pickle.dump({"modelo": self.modelo, "scaler": self.scaler,
                         "decoder": self.decoder_rotulos}, arquivo)

    def carregar(self):
        caminho = os.path.join(config.CONFIG["caminho_modelos"], self.MODELO)
        if not os.path.exists(caminho):
            return False
        with open(caminho, "rb") as arquivo:
            dados = pickle.load(arquivo)
        self.modelo = dados["modelo"]
        self.scaler = dados["scaler"]
        self.decoder_rotulos = dados["decoder"]
        return self.modelo is not None

    def carregar_dados(self):
        caminho = os.path.join(config.CONFIG["caminho_modelos"], self.DADOS)
        if not os.path.exists(caminho):
            return [], []
        with np.load(caminho, allow_pickle=False) as arquivo:
            return arquivo["sequencias"].tolist(), arquivo["rotulos"].tolist()

    def atualizar_catalogo(self, sinal, modo, pessoa):
        caminho = os.path.join(config.CONFIG["caminho_modelos"], self.CATALOGO)
        catalogo = {}
        if os.path.exists(caminho):
            with open(caminho, encoding="utf-8") as arquivo:
                catalogo = json.load(arquivo)
        chave = f"{modo}:{sinal}"
        registro = catalogo.setdefault(chave, {
            "sinal": sinal, "modo": modo, "pessoas": [], "sessoes": 0,
        })
        if pessoa and pessoa not in registro["pessoas"]:
            registro["pessoas"].append(pessoa)
        registro["sessoes"] += 1
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(catalogo, arquivo, ensure_ascii=False, indent=2)
