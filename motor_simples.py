import cv2
import os
import numpy as np

def fabricar_corte_com_legenda(video_path, inicio, fim, legenda):
    """Cria corte com legenda de forma simples"""
    
    print(f"[PROCESSANDO] {inicio}s-{fim}s: {legenda}")
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("[ERRO] Nao conseguiu abrir video")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    start_frame = int(inicio * fps)
    end_frame = int(fim * fps)
    
    # Crop para 9:16
    nova_width = int(h * 9 / 16)
    crop_left = (w - nova_width) // 2
    crop_right = crop_left + nova_width
    
    # Arquivo saida
    nome_saida = f"cortes/corte_{inicio}_leg.avi"
    
    # Writer
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    writer = cv2.VideoWriter(nome_saida, fourcc, fps, (nova_width, h))
    
    if not writer.isOpened():
        print("[ERRO] VideoWriter nao abriu")
        cap.release()
        return
    
    frame_count = 0
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    while frame_count < (end_frame - start_frame):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Crop
        frame_crop = frame[:, crop_left:crop_right]
        
        # Adiciona legenda
        font = cv2.FONT_HERSHEY_SIMPLEX
        fontscale = 1.5
        thickness = 3
        color_text = (65, 255, 0)  # BGR green
        color_outline = (0, 0, 0)   # BGR black
        
        text_size = cv2.getTextSize(legenda, font, fontscale, thickness)[0]
        x = max(10, (nova_width - text_size[0]) // 2)
        y = h - 80
        
        # Contorno
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 1, 2]:
                if dx != 0 or dy != 0:
                    cv2.putText(frame_crop, legenda, (x+dx, y+dy), font, fontscale, color_outline, thickness)
        
        # Texto
        cv2.putText(frame_crop, legenda, (x, y), font, fontscale, color_text, thickness)
        
        # Escreve
        writer.write(frame_crop)
        frame_count += 1
        
        if frame_count % 100 == 0:
            print(f"  {frame_count} frames")
    
    cap.release()
    writer.release()
    
    # Rename
    saida_final = nome_saida.replace('_leg.avi', '.mp4').replace('.mp4', '_temp.mp4')
    os.rename(nome_saida, saida_final)
    
    print(f"[OK] {saida_final}\n")

# PROCESSA CADA CORTE
print("="*60)
print("ADICIONANDO LEGENDAS AOS VIDEOS")
print("="*60 + "\n")

video_principal = "estoque/teste.mp4"

cortes = [
    (10, 25, "ESTRATEGIA INSANA"),
    (40, 55, "MUDOU MINHA VIDA"),
    (80, 95, "RESULTADO FINAL")
]

for ini, fim, legenda in cortes:
    fabricar_corte_com_legenda(video_principal, ini, fim, legenda)

print("\n[CONCLUIDO]")
