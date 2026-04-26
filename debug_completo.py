#!/usr/bin/env python
"""Debug completo da transcricao e renderizacao"""

import cv2
import os
import numpy as np
import subprocess
from PIL import Image, ImageDraw, ImageFont

print("[DEBUG] Iniciando debug...")

# 1. Extrai audio
print("\n[1] Extraindo audio...")
video_path = "estoque/teste.mp4"
audio_path = "debug_audio.wav"

# Tenta com opencv primeiro
cap = cv2.VideoCapture(video_path)
if cap.isOpened():
    print(f"[OK] Video abriu com OpenCV")
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"[INFO] FPS: {fps}, Total frames: {total_frames}")
    cap.release()
else:
    print(f"[ERROR] Nao conseguiu abrir video com OpenCV")

# 2. Testa Whisper
print("\n[2] Testando Whisper...")
try:
    import whisper
    print(f"[OK] Whisper importado")
    
    # Cria audio de teste (gera um beep de 2 segundos)
    import numpy as np
    sample_rate = 16000
    duration = 2
    frequency = 440
    t = np.linspace(0, duration, sample_rate * duration)
    audio_test = np.sin(2 * np.pi * frequency * t) * 0.3
    
    # Salva como WAV
    import scipy.io.wavfile as wavfile
    wavfile.write("test_beep.wav", sample_rate, (audio_test * 32767).astype(np.int16))
    print(f"[OK] Audio teste criado")
    
    # Tenta transcrever
    print(f"[LOAD] Carregando modelo Whisper base (pode levar 1-2 min)...")
    model = whisper.load_model("base")
    print(f"[OK] Modelo carregado")
    
    print(f"[TRANSCRIBE] Transcrevendo audio teste...")
    resultado = model.transcribe("test_beep.wav", language="pt", verbose=False)
    segmentos = resultado.get("segments", [])
    
    print(f"[OK] Resultado: {len(segmentos)} segmentos")
    if segmentos:
        for seg in segmentos[:3]:
            print(f"     [{seg['start']:.2f}s-{seg['end']:.2f}s] {seg['text']}")
    
    # Agora testa com video real
    print(f"\n[3] Transcrevendo video real...")
    print(f"[INFO] Extraindo audio do video (pode levar 30s)...")
    
    # Cria script para extrair audio com ffmpeg-python ou cv2
    # Deixa tentar direto com cv2 se possivel
    print(f"[INFO] Testando extracacao audio...")
    
    # Se ffmpeg nao funcionar, vamos usar uma abordagem alternativa
    # Vamos simplemente transcrever diretamente do video com Whisper
    print(f"[TRANSCRIBE] Transcrevendo video direto...")
    resultado_video = model.transcribe(video_path, language="pt", verbose=True)
    segmentos_video = resultado_video.get("segments", [])
    
    print(f"\n[OK] {len(segmentos_video)} segmentos encontrados no video:")
    if segmentos_video:
        for seg in segmentos_video[:10]:
            print(f"     [{seg['start']:.2f}s-{seg['end']:.2f}s] '{seg['text']}'")
    else:
        print(f"[WARNING] Nenhum segmento encontrado!")
    
except ImportError as e:
    print(f"[ERROR] Whisper nao importado: {e}")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

# 4. Testa renderizacao de texto
print("\n[4] Testando renderizacao de texto...")
try:
    # Cria imagem de teste
    img = Image.new('RGB', (600, 1000), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Carrega fonte
    try:
        fonte = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 32)
    except:
        fonte = ImageFont.load_default()
    
    # Desenha texto
    texto = "TESTE DE LEGENDA VERDE"
    cor_verde = (0, 255, 65)  # Verde #00FF41
    
    bbox = draw.textbbox((0, 0), texto, font=fonte)
    text_width = bbox[2] - bbox[0]
    x = (600 - text_width) // 2
    y = 900
    
    # Contorno
    for adj_x, adj_y in [(-1, -1), (-1, 1), (1, -1), (1, 1), (-2, 0), (2, 0), (0, -2), (0, 2)]:
        draw.text((x + adj_x, y + adj_y), texto, font=fonte, fill=(0, 0, 0))
    
    # Texto colorido
    draw.text((x, y), texto, font=fonte, fill=cor_verde)
    
    img.save("debug_test_legenda.png")
    print(f"[OK] Imagem salva: debug_test_legenda.png")
    
except Exception as e:
    print(f"[ERROR] Erro na renderizacao: {e}")

print("\n[DONE] Debug completo!")
