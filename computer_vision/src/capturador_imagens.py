#!/usr/bin/env python3
"""
Capturador de Imagens para Treinamento
Salva imagens capturadas da webcam em pastas organizadas por classe
Cada pasta em dados_treinamento/ é uma classe
As imagens são salvas como: {classe}_{contador}.jpg
"""

import cv2
import os
import sys
import argparse
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from sistema_libras.utilitarios import UtilitariosMaos
from sistema_libras.classificador import ClassificadorLibras


class CapturadorImagens:
    """Captura e salva imagens de webcam em pastas de classes"""
    
    def __init__(self, caminho_dados, indice_camera=0):
        self.caminho_dados = Path(caminho_dados)
        self.indice_camera = indice_camera
        self.classes = []
        self.classe_atual = 0
        self.contador_atual = {}
        # Utilitários para detectar mãos e (opcionalmente) classificar
        try:
            self.utilitarios = UtilitariosMaos()
        except Exception:
            self.utilitarios = None

        # Carregar classificador se disponível
        try:
            clf = ClassificadorLibras()
            if clf.carregar_modelo():
                self.classificador = clf
            else:
                self.classificador = None
        except Exception:
            self.classificador = None
        
        # Verificar e criar pastas de classes
        self._verificar_pastas()
    
    def _verificar_pastas(self):
        """Verifica se o caminho existe e lista as classes"""
        if not self.caminho_dados.exists():
            print(f"❌ Caminho não encontrado: {self.caminho_dados}")
            print(f"✅ Criando diretório: {self.caminho_dados}")
            self.caminho_dados.mkdir(parents=True, exist_ok=True)
        
        # Encontrar todas as pastas (classes)
        self.classes = sorted([
            d.name for d in self.caminho_dados.iterdir() 
            if d.is_dir()
        ])
        
        if not self.classes:
            print(f"❌ Nenhuma pasta de classe encontrada em: {self.caminho_dados}")
            print("💡 Crie pastas com os nomes das classes:")
            print(f"   mkdir -p {self.caminho_dados}/A")
            print(f"   mkdir -p {self.caminho_dados}/B")
            print(f"   mkdir -p {self.caminho_dados}/C")
            return False
        
        print(f"✅ Classes encontradas: {self.classes}")
        
        # Inicializar contadores para cada classe
        for classe in self.classes:
            pasta_classe = self.caminho_dados / classe
            imagens_existentes = len(list(pasta_classe.glob("*.jpg"))) + \
                                 len(list(pasta_classe.glob("*.png")))
            self.contador_atual[classe] = imagens_existentes
        
        return True
    
    def capturar(self):
        """Loop principal de captura"""
        if not self.classes:
            print("❌ Sem classes para capturar")
            return False
        
        print("\n" + "="*70)
        print("📷 CAPTURADOR DE IMAGENS PARA TREINAMENTO")
        print("="*70)
        
        camera = cv2.VideoCapture(int(self.indice_camera))
        
        if not camera.isOpened():
            print(f"❌ Não foi possível abrir a câmera com índice {self.indice_camera}")
            camera.open()
            return False
        
        # Configurar resolução
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.CONFIG['dimensao_imagem'][0])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CONFIG['dimensao_imagem'][1])
        
        print("\n💡 INSTRUÇÕES:")
        print("   ESPAÇO    - Capturar imagem (salva na pasta da classe)")
        print("   ENTER     - Próxima classe")
        print("   'r'       - Reiniciar contador da classe")
        print("   'q'       - Sair")
        print("-" * 70)
        
        while True:
            if self.classe_atual >= len(self.classes):
                print("\n✅ Todas as classes foram cobertas!")
                break
            
            classe = self.classes[self.classe_atual]
            sucesso, quadro = camera.read()
            
            if not sucesso:
                print("❌ Erro ao capturar da câmera")
                break
            
            # Espelhar imagem
            quadro = cv2.flip(quadro, 1)
            
            # Criar cópia para exibição (com interface)
            quadro_display = quadro.copy()
            
            # Determinar cor do indicador dinamicamente
            indicator_color = (255, 255, 0)  # ciano padrão
            if self.utilitarios is not None:
                quadro_rgb = cv2.cvtColor(quadro, cv2.COLOR_BGR2RGB)
                resultados = self.utilitarios.maos.process(quadro_rgb)
                if resultados.multi_hand_landmarks:
                    altura, largura = quadro.shape[:2]
                    tamanho_relativo = 0.25
                    side = int(min(altura, largura) * tamanho_relativo)
                    cx, cy = largura // 2, altura // 2
                    half = side // 2
                    tl_x, tl_y = cx - half, cy - half
                    br_x, br_y = cx + half, cy + half

                    for marcos_mao in resultados.multi_hand_landmarks:
                        xs = [lm.x for lm in marcos_mao.landmark]
                        ys = [lm.y for lm in marcos_mao.landmark]
                        min_x_px = int(min(xs) * largura)
                        max_x_px = int(max(xs) * largura)
                        min_y_px = int(min(ys) * altura)
                        max_y_px = int(max(ys) * altura)
                        center_x = (min_x_px + max_x_px) // 2
                        center_y = (min_y_px + max_y_px) // 2

                        if (center_x >= tl_x and center_x <= br_x and
                                center_y >= tl_y and center_y <= br_y):
                            # Mão dentro do indicador -> azul
                            indicator_color = (255, 0, 0)
                            # Se houver classificador, testar previsão
                            if self.classificador is not None:
                                caracteristicas = self.utilitarios.extrair_caracteristicas(marcos_mao)
                                label, conf = self.classificador.prever(caracteristicas)
                                if label != "?":
                                    indicator_color = (0, 255, 0)  # verde
                            # Desenhar landmarks APENAS na cópia de exibição
                            try:
                                self.utilitarios.desenhar_landmarks(quadro_display, marcos_mao)
                            except Exception:
                                pass
                            break

            # Desenhar interface apenas na cópia de exibição
            self._desenhar_interface(quadro_display, classe, indicator_color)
            
            cv2.imshow("Capturador de Imagens", quadro_display)
            
            tecla = cv2.waitKey(1) & 0xFF
            
            if tecla == ord(' '):  # ESPAÇO - capturar
                # Salvar apenas a imagem original, sem interface
                self._salvar_imagem(quadro, classe)
            elif tecla == ord('\r') or tecla == ord('\n'):  # ENTER - próxima classe
                self.classe_atual += 1
                print(f"\n{'='*70}")
                if self.classe_atual < len(self.classes):
                    print(f"✅ Avançando para classe: {self.classes[self.classe_atual]}")
            elif tecla == ord('r'):  # 'r' - reiniciar contador
                print(f"\n🔄 Reiniciando contador para {classe}...")
                self.contador_atual[classe] = 0
            elif tecla == ord('q'):  # 'q' - sair
                print("\n👋 Saindo...")
                break
        
        camera.release()
        cv2.destroyAllWindows()
        
        # Sumário final
        self._exibir_sumario()
        
        return True
    
    def _desenhar_interface(self, quadro, classe, indicator_color=None):
        """Desenha interface no canto superior esquerdo"""
        altura, largura = quadro.shape[:2]
        
        # Calcular tamanho do painel (1/4 da largura)
        largura_painel = largura // 4
        altura_painel = 250
        
        # Fundo semi-transparente para o painel
        overlay = quadro.copy()
        cv2.rectangle(overlay, (0, 0), (largura_painel, altura_painel), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, quadro, 0.3, 0, quadro)
        
        # Borda do painel
        cv2.rectangle(quadro, (0, 0), (largura_painel, altura_painel), (0, 255, 0), 2)
        
        # Posicionamento vertical dos itens
        margem_x = 15
        margem_y = 30
        espacamento = 45
        
        # 1. Classe atual
        cv2.putText(quadro, f"CLASSE: {classe}", (margem_x, margem_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 2. Contador
        contador = self.contador_atual[classe]
        cv2.putText(quadro, f"Imagens: {contador}", (margem_x, margem_y + espacamento),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # 3. Progresso de classes
        progresso = f"Classe {self.classe_atual + 1}/{len(self.classes)}"
        cv2.putText(quadro, progresso, (margem_x, margem_y + espacamento * 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 255), 2)
        
        # 4. Instruções (divididas em duas linhas)
        cv2.putText(quadro, "ESPACO: Capturar", (margem_x, margem_y + espacamento * 3),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(quadro, "ENTER: Proxima", (margem_x, margem_y + espacamento * 3 + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(quadro, "R: Reset", (margem_x, margem_y + espacamento * 3 + 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.putText(quadro, "Q: Sair", (margem_x, margem_y + espacamento * 3 + 75),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Indicador central (onde posicionar a mão)
        # Tamanho relativo: 25% do menor lado da imagem
        tamanho_relativo = 0.25
        side = int(min(altura, largura) * tamanho_relativo)
        cx, cy = largura // 2, altura // 2
        half = side // 2
        tl = (cx - half, cy - half)
        br = (cx + half, cy + half)
        cor_indicador = indicator_color if indicator_color is not None else (255, 255, 0)  # ciano em BGR
        espessura = 1  # borda fina
        cv2.rectangle(quadro, tl, br, cor_indicador, espessura, lineType=cv2.LINE_AA)
    
    def _salvar_imagem(self, quadro, classe):
        """Salva a imagem na pasta da classe"""
        pasta_classe = self.caminho_dados / classe
        pasta_classe.mkdir(parents=True, exist_ok=True)
        
        # Calcular corte central com o mesmo tamanho do indicador
        # altura, largura = quadro.shape[:2]
        # tamanho_relativo = 0.25
        # side = int(min(altura, largura) * tamanho_relativo)
        # cx, cy = largura // 2, altura // 2
        # half = side // 2
        # x1 = max(0, cx - half)
        # y1 = max(0, cy - half)
        # x2 = min(largura, cx + half)
        # y2 = min(altura, cy + half)

        # Se o corte for inválido, salva a imagem inteira como fallback
        # if x2 <= x1 or y2 <= y1:
        #     regioesalvar = quadro
        # else:
        #     regioesalvar = quadro[y1:y2, x1:x2]

        # Incrementar contador
        self.contador_atual[classe] += 1
        contador = self.contador_atual[classe]

        # Nome do arquivo
        nome_arquivo = f"{classe}_{contador:04d}.jpg"
        caminho_completo = pasta_classe / nome_arquivo

        # Salvar apenas a região cortada
        # cv2.imwrite(str(caminho_completo), regioesalvar)
        cv2.imwrite(str(caminho_completo), quadro)
        
        print(f"✅ Salvo: {caminho_completo}")

        # print(f"✅ Salvo (cortado): {caminho_completo}  — região {x1},{y1} -> {x2},{y2}")
    
    def _exibir_sumario(self):
        """Exibe sumário de imagens capturadas"""
        print("\n" + "="*70)
        print("📊 SUMÁRIO DE CAPTURA")
        print("="*70)
        
        total = 0
        for classe in self.classes:
            contador = self.contador_atual[classe]
            total += contador
            status = "✅" if contador > 0 else "⚠️"
            print(f"{status} {classe:15} - {contador:4} imagens")
        
        print("-" * 70)
        print(f"📈 Total de imagens: {total}")
        print("="*70 + "\n")


def parse_args():
    """Parse de argumentos da linha de comando"""
    parser = argparse.ArgumentParser(
        description='Capturador de imagens para treinamento de LIBRAS'
    )
    
    parser.add_argument(
        '--camera', 
        type=int, 
        default=0, 
        help='Índice da câmera (padrão: 0)'
    )
    
    parser.add_argument(
        '--caminho',
        type=str,
        default=config.CONFIG['caminho_dados'],
        help=f'Caminho de dados (padrão: {config.CONFIG["caminho_dados"]})'
    )
    
    return parser.parse_args()


def main():
    """Função principal"""
    try:
        args = parse_args()
        
        print("\n" + "╔" + "="*68 + "╗")
        print("║" + " "*68 + "║")
        print("║" + "   📷 CAPTURADOR DE IMAGENS - LIBRAS NAVAL   ".center(68) + "║")
        print("║" + " "*68 + "║")
        print("╚" + "="*68 + "╝\n")
        
        print(f"📁 Caminho: {args.caminho}")
        print(f"📷 Câmera: índice {args.camera}\n")
        
        capturador = CapturadorImagens(args.caminho, args.camera)
        
        if capturador.classes:
            capturador.capturar()
        else:
            print("❌ Nenhuma classe encontrada. Crie as pastas primeiro.")
            sys.exit(1)
    
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
