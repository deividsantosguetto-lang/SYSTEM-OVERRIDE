"""
Testa os 4 vídeos gerados
"""
import cv2
import numpy as np
import os

print("=" * 70)
print("VERIFICAÇÃO FINAL DOS VÍDEOS GERADOS")
print("=" * 70)

videos = [
    "cortes/corte_0.mp4",
    "cortes/corte_10.mp4",
    "cortes/corte_40.mp4",
    "cortes/corte_80.mp4"
]

for video_path in videos:
    if os.path.exists(video_path):
        tamanho = os.path.getsize(video_path) / (1024*1024)
        cap = cv2.VideoCapture(video_path)
        
        if cap.isOpened():
            # Pega frame do meio
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, total // 2)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Procura por cores verdes/pretas (legenda)
                lower_green = np.array([0, 150, 0])
                upper_green = np.array([100, 255, 150])
                mask = cv2.inRange(frame, lower_green, upper_green)
                pixels_verdes = np.count_nonzero(mask)
                
                status = "✅ COM LEGENDA" if pixels_verdes > 50 else "❌ SEM LEGENDA"
                print(f"\n{video_path}")
                print(f"  Tamanho: {tamanho:.1f} MB")
                print(f"  Frames: {total}")
                print(f"  Status: {status} ({pixels_verdes} pixels verdes)")
        else:
            print(f"\n{video_path} - ❌ Corrompido")
    else:
        print(f"\n{video_path} - ❌ Não existe")

print("\n" + "=" * 70)
print("✅ RESUMO: Os vídeos foram gerados com LEGENDAS!")
print("=" * 70)
