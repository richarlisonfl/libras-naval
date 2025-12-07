import os
import warnings

# Suprimir warnings chatos
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Configurações do sistema
CONFIG = {
    'dimensao_imagem': (640, 480),
    'fps_camera': 30,
    'numero_amostras_por_classe': 100,
    'limite_confianca': 0.32,
    'caminho_dados': 'computer_vision/data/to_training/',
    'caminho_modelos': 'computer_vision/data/generated_model/',
    'classes_treinamento': 'AEIOU',
    'numeros_treinamento': '012345'
}

# Criar diretórios se não existirem
os.makedirs(CONFIG['caminho_dados'], exist_ok=True)
os.makedirs(CONFIG['caminho_modelos'], exist_ok=True)