#!/usr/bin/env python3
"""
Script de validação do sistema - verifica se todos os componentes estão funcionando
"""

import sys
import os
import subprocess

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def verificar_modulo(nome_modulo, nome_pacote=None):
    """Verifica se um módulo está instalado"""
    if nome_pacote is None:
        nome_pacote = nome_modulo

    try:
        __import__(nome_modulo)
        print(f" {nome_pacote}: OK")
        return True
    except ImportError:
        print(f" {nome_pacote}: NÃO INSTALADO")
        return False

def verificar_arquivos():
    """Verifica se os arquivos principais existem"""
    arquivos_necessarios = [
        'main.py',
        'src/apps/treinamento_app.py',
        'src/apps/reconhecimento_app.py',
        'src/core/__init__.py',
        'src/core/coletor_dados.py',
        'src/core/classificador.py',
        'src/services/reconhecedor.py',
        'src/core/detector_maos.py',
        'config.py',
        'teste_rapido.py'
    ]

    print("\n" + "="*60)
    print(" VERIFICANDO ARQUIVOS")
    print("="*60)

    todos_existem = True
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f" {arquivo}: OK")
        else:
            print(f" {arquivo}: NÃO ENCONTRADO")
            todos_existem = False

    return todos_existem

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print("\n" + "="*60)
    print(" VERIFICANDO DEPENDÊNCIAS")
    print("="*60)

    dependencias = [
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('mediapipe', 'MediaPipe'),
        ('sklearn', 'Scikit-Learn'),
    ]

    todas_ok = True
    for modulo, nome in dependencias:
        if not verificar_modulo(modulo, nome):
            todas_ok = False

    return todas_ok

def verificar_imports():
    """Verifica se os módulos do projeto podem ser importados"""
    print("\n" + "="*60)
    print(" VERIFICANDO IMPORTS DO PROJETO")
    print("="*60)

    try:
        from src.core.detector_maos import DetectorMaos
        print(" DetectorMaos: OK")
    except Exception as e:
        print(f" DetectorMaos: {e}")
        return False

    try:
        from src.core.classificador import ClassificadorLibras
        print(" ClassificadorLibras: OK")
    except Exception as e:
        print(f" ClassificadorLibras: {e}")
        return False

    try:
        from src.services.reconhecedor import ReconhecedorLibras
        print(" ReconhecedorLibras: OK")
    except Exception as e:
        print(f" ReconhecedorLibras: {e}")
        return False

    try:
        from src.core.coletor_dados import ColetorDadosLibras
        print(" ColetorDadosLibras: OK")
    except Exception as e:
        print(f" ColetorDadosLibras: {e}")
        return False

    return True

def verificar_config():
    """Verifica se o arquivo de configuração está correto"""
    print("\n" + "="*60)
    print("  VERIFICANDO CONFIGURAÇÃO")
    print("="*60)

    try:
        import config
        print(f" Config carregada: OK")
        print(f"   - Dimensão imagem: {config.CONFIG['dimensao_imagem']}")
        print(f"   - Amostras por classe: {config.CONFIG['numero_amostras_por_classe']}")
        print(f"   - Caminho dados: {config.CONFIG['caminho_dados']}")
        print(f"   - Limite confiança: {config.CONFIG['limite_confianca']}")
        return True
    except Exception as e:
        print(f" Erro ao carregar config: {e}")
        return False

def main():
    """Função principal"""
    print("\n" + "╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "    VALIDAÇÃO DO SISTEMA - LibrasNaval".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝\n")

    # Executar verificações
    deps_ok = verificar_dependencias()
    arquivos_ok = verificar_arquivos()
    config_ok = verificar_config()
    imports_ok = verificar_imports()

    # Resumo
    print("\n" + "="*60)
    print(" RESUMO DA VALIDAÇÃO")
    print("="*60)
    print(f"Dependências: {' OK' if deps_ok else ' FALTANDO'}")
    print(f"Arquivos: {' OK' if arquivos_ok else ' FALTANDO'}")
    print(f"Configuração: {' OK' if config_ok else ' ERRO'}")
    print(f"Imports: {' OK' if imports_ok else ' ERRO'}")

    if deps_ok and arquivos_ok and config_ok and imports_ok:
        print("\n" + "="*60)
        print(" SISTEMA PRONTO PARA USO!")
        print("="*60)
        print("\n▶  Execute: python main.py")
        print("\nPara mais informações, veja: README_MENU.md\n")
        return 0
    else:
        print("\n" + "="*60)
        print("  PROBLEMAS DETECTADOS")
        print("="*60)
        if not deps_ok:
            print("\n Para instalar as dependências, execute:")
            print("   pip install -r requirements.txt")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())
