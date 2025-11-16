#!/usr/bin/env python3
"""
Treinamento facilitado - versão adaptada com suporte a webcam configurável e pastas de imagens
Permite:
- Treinar com webcam (índice configurável)
- Treinar com imagens de pastas (cada pasta = classe)
"""

import sys
import os
import time
import argparse
import cv2
import numpy as np
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sistema_libras.coletor_dados import ColetorDadosLibras
from sistema_libras.classificador import ClassificadorLibras
from sistema_libras.utilitarios import UtilitariosMaos
import config


class TreinamentoAdaptado:
    """Classe para gerenciar treinamento adaptado"""
    
    def __init__(self, indice_camera=0):
        self.indice_camera = indice_camera
        self.utilitarios = UtilitariosMaos()
        self.dados = []
        self.rotulos = []
    
    def treinar_com_webcam(self, classes, amostras_por_classe=5):
        """Treina utilizando webcam com índice configurável"""
        print(f"\n🎯 Treinando com webcam (índice {self.indice_camera}): {classes}")
        print(f"📸 Amostras por classe: {amostras_por_classe}")
        print("-" * 60)
        
        # Configurar número reduzido de amostras
        config_original = config.CONFIG['numero_amostras_por_classe']
        config.CONFIG['numero_amostras_por_classe'] = amostras_por_classe
        
        coletor = ColetorDadosLibras(indice_camera=self.indice_camera)
        
        for classe in classes:
            print(f"\n📝 Classe atual: {classe}")
            print("💡 Posicione a mão e pressione ESPAÇO para capturar")
            print("   Pressione 's' para pular esta classe")
            print("   Pressione 'q' para sair")
            print("-" * 60)
            
            if not self._coletar_classe_webcam(classe, amostras_por_classe):
                print("⏹️ Coleta interrompida")
                config.CONFIG['numero_amostras_por_classe'] = config_original
                return False
        
        # Restaurar configuração original
        config.CONFIG['numero_amostras_por_classe'] = config_original
        
        # Treinar modelo
        return self._treinar_modelo()
    
    def treinar_com_pastas(self, caminho_pastas):       
        caminho_base = Path(caminho_pastas)
        
        # Encontrar todas as pastas (classes)
        classes = [d.name for d in caminho_base.iterdir() if d.is_dir()]
        
        if not classes:
            print(f"❌ Nenhuma pasta encontrada em: {caminho_pastas}")
            return False
        
        print(f"📚 Classes encontradas: {classes}")
        print(f"📊 Total: {len(classes)} classes")
        print("-" * 60)
        
        for classe in sorted(classes):
            pasta_classe = caminho_base / classe
            imagens = list(pasta_classe.glob("*.jpg")) + list(pasta_classe.glob("*.png")) + list(pasta_classe.glob("*.jpeg"))
            
            if not imagens:
                print(f"⚠️  Nenhuma imagem encontrada em {classe}, pulando...")
                continue
            
            print(f"\n📝 Classe: {classe}")
            print(f"📸 Imagens encontradas: {len(imagens)}")
            
            for idx, caminho_imagem in enumerate(imagens, 1):
                try:
                    imagem = cv2.imread(str(caminho_imagem))
                    if imagem is None:
                        print(f"   ⚠️  Não foi possível ler: {caminho_imagem.name}")
                        continue
                    
                    imagem = cv2.flip(imagem, 1)
                    imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
                    resultados = self.utilitarios.maos.process(imagem_rgb)
                    
                    if resultados.multi_hand_landmarks:
                        # Usar o primeiro marcador de mão
                        marcos_mao = resultados.multi_hand_landmarks[0]
                        caracteristicas = self.utilitarios.extrair_caracteristicas(marcos_mao)
                        self.dados.append(caracteristicas)
                        self.rotulos.append(classe)
                        print(f"   ✅ {idx}. {caminho_imagem.name} - OK")
                    else:
                        print(f"   ⚠️  {idx}. {caminho_imagem.name} - Mão não detectada")
                        
                except Exception as e:
                    print(f"   ❌ {idx}. {caminho_imagem.name} - Erro: {e}")
        
        # Treinar modelo
        return self._treinar_modelo()
    
    def _coletar_classe_webcam(self, classe, amostras_por_classe):
        """Coleta amostras para uma classe via webcam"""
        contador_amostras = 0
        
        camera = cv2.VideoCapture(self.indice_camera)
        
        if not camera.isOpened():
            print(f"❌ Não foi possível abrir a câmera com índice {self.indice_camera}")
            return False
        
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CONFIG['dimensao_imagem'][0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CONFIG['dimensao_imagem'][1])
        
        while contador_amostras < amostras_por_classe:
            sucesso, quadro = camera.read()
            if not sucesso:
                print("❌ Erro ao capturar da câmera")
                camera.release()
                return False
            
            quadro = cv2.flip(quadro, 1)
            quadro_rgb = cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)
            resultados = self.utilitarios.maos.process(quadro_rgb)
            
            # Interface de coleta
            cv2.putText(quadro, f"CLASSE: {classe}", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(quadro, f"AMOSTRAS: {contador_amostras}/{amostras_por_classe}", 
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
                caracteristicas = self.utilitarios.extrair_caracteristicas(resultados.multi_hand_landmarks[0])
                self.dados.append(caracteristicas)
                self.rotulos.append(classe)
                contador_amostras += 1
                print(f"✅ Amostra {contador_amostras} capturada para {classe}")
            elif tecla == ord('s'):  # Pular esta classe
                camera.release()
                cv2.destroyAllWindows()
                return True
            elif tecla == ord('q'):  # Sair completamente
                camera.release()
                cv2.destroyAllWindows()
                return False
        
        camera.release()
        cv2.destroyAllWindows()
        return True
    
    def _treinar_modelo(self):
        """Treina o modelo com os dados coletados"""
        if len(self.dados) == 0:
            print("❌ Nenhum dado coletado para treinamento")
            return False
        
        print(f"\n🧠 Treinando modelo com {len(self.dados)} amostras...")
        print(f"📚 Classes: {set(self.rotulos)}")
        print("-" * 60)
        
        classificador = ClassificadorLibras()
        
        try:
            start_time = time.perf_counter()
            precisao = classificador.treinar(self.dados, self.rotulos)
            duracao_treinamento = time.perf_counter() - start_time
            
            print(f"✅ Modelo treinado com sucesso!")
            print(f"📊 Precisão: {precisao:.3%}")
            print(f"⏱️ Tempo de treinamento: {duracao_treinamento:.2f}s")
            
            classificador.salvar_modelo()
            print(f"💾 Modelo salvo!")
            
            return True
        except Exception as e:
            print(f"❌ Erro ao treinar modelo: {e}")
            import traceback
            traceback.print_exc()
            return False


def parse_args():
    """Parse de argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Treinamento de LIBRAS - versão adaptada')
    
    parser.add_argument('--camera', type=int, default=0, help='Índice da câmera (padrão: 0)')
    parser.add_argument('--modo', choices=['webcam', 'pastas'], default='webcam', help='Modo de treinamento')
    parser.add_argument('--caminho', type=str, default='dados_treinamento', help='Caminho das pastas para treinamento')
    
    return parser.parse_args()

class TreinamentoApp:
    """Classe que encapsula modos de treinamento e interface interativa.

    Uso:
        app = TreinamentoApp(camera=0)
        app.run(mode='webcam')  # modo 'webcam'|'pastas'|None (interativo)
    """

    def __init__(self, camera: int = 0):
        self.camera = int(camera)

    def modo_webcam(self, classes: str = None, amostras_por_classe: int = None):
        """Executa o modo webcam. Se classes não informadas, pergunta ao usuário.

        classes: string com caracteres (ex: 'AEIOU' ou 'ABC123') ou None
        amostras_por_classe: int ou None
        """

        treinador = TreinamentoAdaptado(self.camera)

        if classes is None:
            print("\nEscolha uma opção fácil:")
            print("1. Treinar apenas vogais (A E I O U) - 5 amostras cada")
            print("2. Treinar meus próprios caracteres")
            print("3. Usar treinamento completo")
            opcao = input("\nDigite sua opção (1-3): ").strip()

            if opcao == "1":
                classes = "AEIOU"
                amostras = 5
            elif opcao == "2":
                letras = input("Digite as letras/números (ex: ABC123): ").strip().upper()
                if not letras:
                    print("❌ Nenhum caractere digitado")
                    return False
                classes = letras
                amostras = input("Amostras por classe (padrão 5): ").strip()
                amostras = int(amostras) if amostras.isdigit() else 5
            elif opcao == "3":
                print("⚠️  Treinamento completo - isso pode levar algum tempo!")
                classes = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                amostras = 10
            else:
                print("❌ Opção inválida")
                return False
        else:
            amostras = amostras_por_classe or config.CONFIG.get('numero_amostras_por_classe', 5)

        sucesso = treinador.treinar_com_webcam(classes, amostras)

        if sucesso:
            print("\nTreinamento finalizado com sucesso!")
        return sucesso

    def modo_pastas(self, caminho: str = None):
        """Executa o modo pastas. Se caminho não informado, pergunta ao usuário."""

        if not os.path.exists(caminho):
            print(f"❌ Caminho não encontrado: {caminho}")
            return False

        treinador = TreinamentoAdaptado(self.camera)
        sucesso = treinador.treinar_com_pastas(caminho)

        if sucesso:
            print("\n🎉 Parabéns! Você completou o treinamento com imagens!")
            print("👉 Agora teste com o modo de reconhecimento!")
        return sucesso

    def menu_interativo(self):
        """Menu interativo para seleção de modo de treinamento"""
        while True:
            print("\n" + "="*60)
            print("🎓 TREINAMENTO FACILITADO DE LIBRAS")
            print("="*60)
            print("\n1. 📷 Treinar com Webcam")
            print("2. 📁 Treinar com Imagens de Pastas")
            print("3. 🚪 Sair")
            print("-"*60)

            opcao = input("Escolha uma opção (1-3): ").strip()

            if opcao == "1":
                return self.modo_webcam()
            elif opcao == "2":
                return self.modo_pastas()
            elif opcao == "3":
                print("👋 Saindo...")
                return False
            else:
                print("❌ Opção inválida!")

    def run(self, mode: str = None, caminho: str = None, classes: str = None, amostras: int = None):
        """Executa o modo escolhido.

        mode: 'webcam'|'pastas'|None. If None, interactive menu is shown.
        """
        if mode == 'webcam':
            return self.modo_webcam(classes, amostras)
        elif mode == 'pastas':
            return self.modo_pastas(caminho)
        else:
            return self.menu_interativo()


def main():
    """Função principal"""
    try:
        args = parse_args()
        print("="*60)
        print("🎓 SISTEMA DE TREINAMENTO - LIBRAS NAVAL")
        print("="*60)
        print(f"📷 Câmera: índice {args.camera}")

        app = TreinamentoApp(camera=args.camera)
        if args.modo == 'webcam':
            app.run(mode='webcam')
        elif args.modo == 'pastas':
            app.run(mode='pastas', caminho=args.caminho)
        else:
            app.run()

    except KeyboardInterrupt:
        print("\n🛑 Programa interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
if __name__ == "__main__":
    main()
