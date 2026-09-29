import os
import warnings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Suprimir warnings chatos
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Configurações do sistema
CONFIG = {
    'dimensao_imagem': (640, 480),
    'fps_camera': 30,
    'limite_confianca': 0.60,
    'janela_dinamica': 45,
    'limiar_movimento': 0.008,
    'limite_confianca_dinamico': 0.55,
    'limite_confianca_envio': 0.80,
    'limite_confianca_iniciar': 0.75,
    'intervalo_envio_sinal': 3.0,
    'caminho_modelos': os.path.join(BASE_DIR, 'data', 'generated_model')
}

# Criar diretórios se não existirem
os.makedirs(CONFIG['caminho_modelos'], exist_ok=True)