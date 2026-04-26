#!/usr/bin/env python
"""Ultima tentativa - adiciona legendas e salva em formato diferente"""

import cv2
import os
import numpy as np

print("[TESTE] Abrindo primeiro video...")

cap = cv2.VideoCapture("cortes/corte_10.mp4")

if not cap.isOpened():
    print("[FAIL] Nao conseguiu abrir corte_10.mp4")
    exit(1)

print("[OK] Video abriu")

fps = cap.get(cv2.CAP_PROP_FPS)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"[INFO] {w}x{h} @ {fps}fps")

# Tenta criar writer
print("[TESTE] Criando VideoWriter com MJPG...")
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
writer = cv2.VideoWriter("test_output.avi", fourcc, fps, (w, h))

if not writer.isOpened():
    print("[FAIL] Nao conseguiu criar writer")
    exit(1)

print("[OK] Writer criado")

# Pega um frame
ret, frame = cap.read()
if ret:
    print("[OK] Frame lido")
    
    # Adiciona texto simples
    cv2.putText(frame, "TESTE", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 65), 3)
    
    # Tenta escrever
    writer.write(frame)
    print("[OK] Frame escrito no writer")
else:
    print("[FAIL] Nao conseguiu ler frame")

cap.release()
writer.release()

if os.path.exists("test_output.avi"):
    tamanho = os.path.getsize("test_output.avi")
    print(f"[SUCCESS] test_output.avi criado ({tamanho} bytes)")
    
    # Tenta abrir
    cap_test = cv2.VideoCapture("test_output.avi")
    if cap_test.isOpened():
        print("[OK] test_output.avi pode ser aberto")
        cap_test.release()
    else:
        print("[FAIL] test_output.avi nao pode ser aberto")
else:
    print("[FAIL] test_output.avi nao foi criado")
