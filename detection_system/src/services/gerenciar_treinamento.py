import json
import os

import config
from src.core.classificador import ClassificadorLibras
from src.core.classificador_temporal import ClassificadorTemporal


class GerenciadorTreinamento:
    """Consulta e remove classes de treinamento, mantendo os modelos consistentes."""

    CATALOGO = ClassificadorTemporal.CATALOGO

    @staticmethod
    def listar_sinais():
        caminho = os.path.join(config.CONFIG["caminho_modelos"], GerenciadorTreinamento.CATALOGO)
        if not os.path.exists(caminho):
            return []

        with open(caminho, encoding="utf-8") as arquivo:
            catalogo = json.load(arquivo)
        return sorted(
            catalogo.values(),
            key=lambda registro: (registro["modo"], registro["sinal"]),
        )

    def excluir_sinal(self, modo, sinal):
        if modo == "estatico":
            removidas = self._excluir_estatico(sinal)
        elif modo == "dinamico":
            removidas = self._excluir_dinamico(sinal)
        else:
            raise ValueError("O modo deve ser estatico ou dinamico.")

        self._remover_do_catalogo(modo, sinal)
        return removidas

    def _excluir_estatico(self, sinal):
        classificador = ClassificadorLibras()
        carregado = classificador.carregar_dados_treinamento()
        if carregado is None:
            return 0

        dados, rotulos, grupos = carregado
        indices_mantidos = [
            indice for indice, rotulo in enumerate(rotulos) if rotulo != sinal
        ]
        removidas = len(rotulos) - len(indices_mantidos)
        if removidas == 0:
            return 0

        dados_restantes = [dados[indice] for indice in indices_mantidos]
        rotulos_restantes = [rotulos[indice] for indice in indices_mantidos]
        grupos_restantes = (
            [grupos[indice] for indice in indices_mantidos]
            if grupos is not None
            else None
        )
        self._salvar_e_retornar_modelo_estatico(
            classificador, dados_restantes, rotulos_restantes, grupos_restantes
        )
        return removidas

    def _excluir_dinamico(self, sinal):
        classificador = ClassificadorTemporal()
        sequencias, rotulos = classificador.carregar_dados()
        indices_mantidos = [
            indice for indice, rotulo in enumerate(rotulos) if rotulo != sinal
        ]
        removidas = len(rotulos) - len(indices_mantidos)
        if removidas == 0:
            return 0

        sequencias_restantes = [sequencias[indice] for indice in indices_mantidos]
        rotulos_restantes = [rotulos[indice] for indice in indices_mantidos]
        self._salvar_e_retornar_modelo_dinamico(
            classificador, sequencias_restantes, rotulos_restantes
        )
        return removidas

    def _salvar_e_retornar_modelo_estatico(
        self, classificador, dados, rotulos, grupos
    ):
        if not dados:
            self._remover_arquivo(ClassificadorLibras.NOME_DADOS)
            self._remover_arquivo(ClassificadorLibras.NOME_MODELO)
            return

        classificador.salvar_dados_treinamento(dados, rotulos, grupos=grupos)
        if self._dados_suficientes_para_treino(rotulos):
            classificador.treinar(dados, rotulos, grupos=grupos)
            classificador.salvar_modelo()
        else:
            self._remover_arquivo(ClassificadorLibras.NOME_MODELO)

    def _salvar_e_retornar_modelo_dinamico(self, classificador, sequencias, rotulos):
        if not sequencias:
            self._remover_arquivo(ClassificadorTemporal.DADOS)
            self._remover_arquivo(ClassificadorTemporal.MODELO)
            return

        classificador.salvar_dados(sequencias, rotulos)
        if self._dados_suficientes_para_treino(rotulos):
            classificador.treinar(sequencias, rotulos)
            classificador.salvar(sequencias, rotulos)
        else:
            self._remover_arquivo(ClassificadorTemporal.MODELO)

    @staticmethod
    def _dados_suficientes_para_treino(rotulos):
        classes = set(rotulos)
        return (
            len(classes) >= 2
            and all(rotulos.count(classe) >= 2 for classe in classes)
        )

    def _remover_do_catalogo(self, modo, sinal):
        caminho = os.path.join(config.CONFIG["caminho_modelos"], self.CATALOGO)
        if not os.path.exists(caminho):
            return

        with open(caminho, encoding="utf-8") as arquivo:
            catalogo = json.load(arquivo)
        catalogo.pop(f"{modo}:{sinal}", None)
        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(catalogo, arquivo, ensure_ascii=False, indent=2)

    @staticmethod
    def _remover_arquivo(nome_arquivo):
        caminho = os.path.join(config.CONFIG["caminho_modelos"], nome_arquivo)
        if os.path.exists(caminho):
            os.remove(caminho)
