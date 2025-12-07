class Camera:
    def selecionar_indice_camera():
        """Permite ao usuário selecionar o índice da câmera"""
        print("\n" + "-"*60)
        print("🎥 SELEÇÃO DE CÂMERA")
        print("-"*60)
        
        import cv2
        
        cameras_disponiveis = []
        print("🔍 Procurando câmeras disponíveis...")
        
        for i in range(10):
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                cameras_disponiveis.append(i)
                print(f"   ✅ Câmera {i} encontrada")
                camera.release()
            else:
                camera.release()
        
        if not cameras_disponiveis:
            print("   ❌ Nenhuma câmera encontrada!")
            return None
        
        print("\nCâmeras disponíveis:", cameras_disponiveis)
        
        while True:
            try:
                if cameras_disponiveis:
                    return cameras_disponiveis[0]

                indice = int(input(f"Digite o índice da câmera (padrão 0): ").strip() or "0")
                if indice in cameras_disponiveis:
                    print(f"✅ Câmera {indice} selecionada!")
                    return indice
                else:
                    print(f"❌ Câmera {indice} não encontrada. Tente novamente.")
            except ValueError:
                print("❌ Digite um número válido.")