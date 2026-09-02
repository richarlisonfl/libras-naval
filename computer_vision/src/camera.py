class Camera:
    @staticmethod
    def selecionar_indice_camera():
        """Detecta câmeras disponíveis e permite selecionar uma delas."""
        print("\n" + "-"*60)
        print("SELEÇÃO DE CÂMERA")
        print("-"*60)
        
        import cv2
        
        cameras_disponiveis = []
        print("Procurando câmeras disponíveis...")
        
        for i in range(10):
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                cameras_disponiveis.append(i)
                print(f"    Câmera {i} encontrada")
                camera.release()
            else:
                camera.release()
        
        if not cameras_disponiveis:
            print("    Nenhuma câmera encontrada!")
            return None
        
        print("\nCâmeras disponíveis:", cameras_disponiveis)
        
        while True:
            try:
                indice = int(input(
                    f"Digite o índice da câmera (padrão {cameras_disponiveis[0]}): "
                ).strip() or str(cameras_disponiveis[0]))
            except ValueError:
                print(" Digite um número válido.")
                continue

            if indice in cameras_disponiveis:
                print(f" Câmera {indice} selecionada!")
                return indice

            print(f" Câmera {indice} não encontrada. Tente novamente.")