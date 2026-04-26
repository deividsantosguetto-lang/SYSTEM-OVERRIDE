#!/usr/bin/env python
"""Teste de transcrição com Whisper"""

import subprocess
import os

# Extrai áudio do vídeo
video_path = "estoque/teste.mp4"
audio_path = "cortes/teste_audio.wav"

print("Extraindo audio...")
ffmpeg_path = os.path.abspath("ffmpeg.exe")
cmd = [ffmpeg_path, "-i", video_path, "-q:a", "9", "-n", "-vn", audio_path]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
if os.path.exists(audio_path):
    print(f"Audio extraido: {audio_path}")
else:
    print(f"Falha na extracao: {result.stderr}")
    exit(1)

# Tenta importar Whisper
print("\nTentando importar Whisper...")
try:
    import whisper
    print("Whisper importado")
except ImportError as e:
    print(f"Whisper nao encontrado: {e}")
    print("Instalando... pip install openai-whisper")
    os.system("pip install openai-whisper")
    import whisper

# Transcreve
print("\nTranscrevendo audio (pode levar 2-3 minutos)...")
try:
    model = whisper.load_model("base")
    resultado = model.transcribe(audio_path, language="pt")
    
    print(f"\nTranscricao completa!")
    print(f"Segmentos: {len(resultado['segments'])}\n")
    
    for seg in resultado["segments"][:5]:  # Mostra primeiros 5
        print(f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
    
    # Limpa
    os.remove(audio_path)
    
except Exception as e:
    print(f"Erro na transcricao: {e}")
    import traceback
    traceback.print_exc()
