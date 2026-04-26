#!/usr/bin/env python
"""Verifica se legendas foram realmente renderizadas nos vídeos"""

import cv2
import os

def verificar_legendas(video_path):
    """Analisa frames do vídeo para detectar legendas"""
    print(f"\n🎬 Analisando: {video_path}")
    
    if not os.path.exists(video_path):
        print(f"❌ Arquivo não encontrado")
        return False
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Não consegui abrir o vídeo")
        return False
    
    frame_count = 0
    legendas_encontradas = 0
    
    # Verifica 30 frames distribuídos no vídeo
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    passo = max(1, total_frames // 30)
    
    print(f"  Total de frames: {total_frames}")
    print(f"  Verificando cada {passo} frames...")
    
    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_num % passo == 0:
            # Procura por pixels verdes (#00FF41 = R:0 G:255 B:65)
            # Em BGR fica B:65 G:255 R:0
            verde_lower = (50, 240, 0)
            verde_upper = (80, 255, 20)
            
            # Cria máscara de pixels verdes
            import numpy as np
            mask = cv2.inRange(frame, verde_lower, verde_upper)
            green_pixels = cv2.countNonZero(mask)
            
            if green_pixels > 100:  # Mais de 100 pixels verdes
                legendas_encontradas += 1
                print(f"  ✅ Frame {frame_num}: {green_pixels} pixels verdes encontrados")
        
        frame_count += 1
        frame_num += 1
    
    cap.release()
    
    print(f"  Frames analisados: {frame_count}")
    print(f"  Frames com legenda: {legendas_encontradas}/{frame_count//passo}")
    
    return legendas_encontradas > 0

# Verifica todos os vídeos
print("=" * 70)
print("VERIFICANDO LEGENDAS NOS VÍDEOS")
print("=" * 70)

videos = [
    "cortes/corte_10.mp4",
    "cortes/corte_40.mp4",
    "cortes/corte_80.mp4"
]

for video in videos:
    if os.path.exists(video):
        tem_legenda = verificar_legendas(video)
        if not tem_legenda:
            print(f"  ⚠️ SEM LEGENDAS DETECTADAS!")
    else:
        print(f"\n❌ {video} não existe")

print("\n" + "=" * 70)
