"""
Extrai frame do vídeo gerado para verificar se legenda está lá
"""
import cv2
import os

print("=" * 70)
print("VERIFICANDO VÍDEO GERADO")
print("=" * 70)

video = "cortes/corte_0.mp4"

if os.path.exists(video):
    cap = cv2.VideoCapture(video)
    
    if cap.isOpened():
        # Pega frame do meio do vídeo
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_do_meio = total_frames // 2
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_do_meio)
        
        ret, frame = cap.read()
        
        if ret:
            # Salva a imagem
            cv2.imwrite("debug_frames/frame_do_video.jpg", frame)
            print(f"✓ Frame extraído do vídeo")
            print(f"  Total de frames: {total_frames}")
            print(f"  Frame extraído: {frame_do_meio}")
            print(f"  Resolução: {frame.shape[1]}x{frame.shape[0]}")
            print(f"\n✅ Imagem salva: debug_frames/frame_do_video.jpg")
            print("\n👉 ABRA ESTA IMAGEM E VEJA SE TEM LEGENDA!")
        else:
            print("❌ Não conseguiu ler frame")
        
        cap.release()
    else:
        print("❌ Não conseguiu abrir o vídeo")
else:
    print("❌ Vídeo não encontrado")
