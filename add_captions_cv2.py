#!/usr/bin/env python
"""Adiciona legendas com cv2.putText diretamente"""

import cv2
import os

def add_caption_cv2(video_file, caption_text):
    """Adiciona legenda usando cv2.putText"""
    
    print(f"[OPEN] {video_file}")
    cap = cv2.VideoCapture(video_file)
    
    if not cap.isOpened():
        print(f"[FAIL] Nao conseguiu abrir")
        return False
    
    # Propriedades
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"[INFO] {width}x{height}, {total} frames, {fps}fps")
    
    # Writer MJPEG
    temp_file = f"temp_{os.path.basename(video_file)}"
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(temp_file, fourcc, fps, (width, height))
    
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Adiciona texto com cv2
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 3
        color_text = (65, 255, 0)  # BGR: verde #00FF41
        color_outline = (0, 0, 0)  # BGR: preto
        
        # Tamanho do texto
        text_size = cv2.getTextSize(caption_text, font, font_scale, thickness)[0]
        text_x = (width - text_size[0]) // 2
        text_y = height - 80
        
        # Contorno preto (desenhado multiplas vezes)
        for dx in [-2, -1, 1, 2]:
            for dy in [-2, -1, 1, 2]:
                if dx != 0 or dy != 0:
                    cv2.putText(frame, caption_text, 
                              (text_x + dx, text_y + dy), 
                              font, font_scale, color_outline, thickness)
        
        # Texto verde
        cv2.putText(frame, caption_text, 
                   (text_x, text_y), 
                   font, font_scale, color_text, thickness)
        
        out.write(frame)
        
        frame_count += 1
        if frame_count % 100 == 0:
            print(f"  {frame_count}/{total}")
    
    cap.release()
    out.release()
    
    # Replace original
    if os.path.exists(temp_file):
        os.remove(video_file)
        os.rename(temp_file, video_file)
        print(f"[DONE] {video_file}\n")
        return True
    else:
        print(f"[ERROR] Temp file nao criado\n")
        return False

# Processa
print("[START] Adicionando legendas com cv2...\n")

videos_legendas = [
    ("cortes/corte_10.mp4", "ESTRATEGIA INSANA"),
    ("cortes/corte_40.mp4", "MUDOU MINHA VIDA"),
    ("cortes/corte_80.mp4", "RESULTADO FINAL")
]

for video, legenda in videos_legendas:
    if os.path.exists(video):
        add_caption_cv2(video, legenda)
    else:
        print(f"[SKIP] {video} nao existe\n")

print("[SUCCESS] LEGENDAS ADICIONADAS!")
