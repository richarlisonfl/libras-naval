import os
import numpy as np
from .coletor_dados import ColetorDadosLibras
from .classificador import ClassificadorLibras
import config

class TreinamentoIncremental:
    def __init__(self):
        self.coletor = ColetorDadosLibras()
        self.classificador = ClassificadorLibras()
        dados_salvos = self.classificador.carregar_dados_treinamento()
        if dados_salvos is None:
            self.classes_treinadas = set()
        else:
            self.coletor.dados, self.coletor.rotulos, _ = dados_salvos
            self.classes_treinadas = set(self.coletor.rotulos)
            print(
                f" Dados carregados: {len(self.coletor.dados)} amostras, "
                f"{len(self.classes_treinadas)} classes"
            )

    def treinar_grupo(self, grupo_classes, amostras_por_classe=5):
        """Treina um grupo específico de classes"""
        print(f" Treinando grupo: {grupo_classes}")

        # Coletar apenas classes não treinadas
        classes_para_treinar = [c for c in grupo_classes if c not in self.classes_treinadas]

        if not classes_para_treinar:
            print(" Todas as classes deste grupo já foram treinadas!")
            return True

        # Configurar número de amostras
        config_original = config.CONFIG['numero_amostras_por_classe']
        config.CONFIG['numero_amostras_por_classe'] = amostras_por_classe

        try:
            for classe in classes_para_treinar:
                print(f"\n Coletando {amostras_por_classe} amostras para: {classe}")
                quantidade_anterior = len(self.coletor.dados)
                if not self.coletor.coletar_classe(classe):
                    print(" Coleta interrompida")
                    return False
                if len(self.coletor.dados) > quantidade_anterior:
                    self.classes_treinadas.add(classe)
        finally:
            config.CONFIG['numero_amostras_por_classe'] = config_original

        # Treinar modelo com TODOS os dados acumulados
        if len(self.coletor.dados) > 0:
            print("\n Atualizando modelo com todos os dados...")
            precisao = self.classificador.treinar(self.coletor.dados, self.coletor.rotulos)
            self.classificador.salvar_dados_treinamento(
                self.coletor.dados,
                self.coletor.rotulos,
            )
            self.classificador.salvar_modelo()
            print(f" Modelo atualizado! Precisão: {precisao:.3f}")

        return True

    def treinar_por_fases(self):
        """Treinamento dividido em fases fáceis"""
        fases = {
            "Fase 1 - Vogais": "AEIOU",
            "Fase 2 - Consoantes simples": "BCDFG",
            "Fase 3 - Mais consoantes": "HJLMN",
            "Fase 4 - Restante": "PQRSTUVWXYZ",
            "Fase 5 - Números 0-4": "01234",
            "Fase 6 - Números 5-9": "56789"
        }

        for nome_fase, classes in fases.items():
            print(f"\n{'='*50}")
            print(f"{nome_fase}")
            print(f"{'='*50}")

            if not self.treinar_grupo(classes, amostras_por_classe=5):
                print("Treinamento interrompido.")
                break

            input("Pressione Enter para próxima fase...")