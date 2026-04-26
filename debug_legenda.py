"""
Debug - extrai frames, coloca legenda, salva imagens
"""
import cv2
import os

print("=" * 70)
print("DEBUG - TESTANDO LEGENDA EM FRAMES")
print("=" * 70)

video = "estoque/teste.mp4"
cap = cv2.VideoCapture(video)

if not cap.isOpened():
    print(f"❌ Não conseguiu abrir {video}")
else:
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"✓ Vídeo: {w}x{h}, FPS: {fps}")
    
    # Corte vertical 9:16
    nova_largura = int(h * 9 / 16)
    crop_left = (w - nova_largura) // 2
    crop_right = crop_left + nova_largura
    
    print(f"✓ Corte: {nova_largura}x{h}")
    
    # Cria pasta
    if not os.path.exists("debug_frames"):
        os.makedirs("debug_frames")
    
    # Extrai primeiros 3 frames
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    for i in range(3):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Crop
        frame_crop = frame[:, crop_left:crop_right]
        
        # DESENHA LEGENDA BIG
        texto = "TESTE DE LEGENDA 🔥"
        
        altura, largura = frame_crop.shape[:2]
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontscale = 4.0  # MUITO GRANDE
        thickness = 5
        
        (text_width, text_height), baseline = cv2.getTextSize(
            "TESTE DE LEGENDA", font, fontscale, thickness
        )
        
        x = (largura - text_width) // 2
        y = altura - 150
        
        print(f"\n Frame {i}:")
        print(f"  - Posição: ({x}, {y})")
        print(f"  - Dimensões do texto: {text_width}x{text_height}")
        
        # Desenha contorno preto FORTE
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                cv2.putText(frame_crop, "TESTE DE LEGENDA", (x + dx, y + dy),
                          font, fontscale, (0, 0, 0), thickness + 3)
        
        # Desenha texto verde BRILHANTE
        cv2.putText(frame_crop, "TESTE DE LEGENDA", (x, y),
                   font, fontscale, (0, 255, 0), thickness)
        
        # Salva imagem
        saida = f"debug_frames/frame_{i:03d}.jpg"
        cv2.imwrite(saida, frame_crop)
        print(f"  ✓ Salvo: {saida}")
    
    cap.release()
    
    print("\n" + "=" * 70)
    print("✅ Verifique as imagens em debug_frames/")
    print("   Se a legenda aparecer nas imagens, o problema é no vídeo")
    print("   Se não aparecer, o cv2.putText está falhando")
    print("=" * 70)
