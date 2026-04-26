import sys

print("TESTE RAPIDO")
print(f"Python: {sys.version}")

# Teste de imports
imports_ok = []
imports_erro = []

libs = [
    "streamlit",
    "flask", 
    "yt_dlp",
    "google.generativeai",
    "dotenv",
    "whisper",
    "cv2",
    "PIL",
    "numpy"
]

for lib in libs:
    try:
        __import__(lib)
        imports_ok.append(lib)
    except:
        imports_erro.append(lib)

print(f"\nOK: {len(imports_ok)}")
print(f"FALTA: {len(imports_erro)}")

if imports_erro:
    print(f"\nFaltando: {', '.join(imports_erro)}")

# Teste .env
import os
if os.path.exists(".env"):
    print("\n.env: OK")
else:
    print("\n.env: FALTA")

# Teste ffmpeg
if os.path.exists("ffmpeg.exe"):
    print("ffmpeg.exe: OK")
else:
    print("ffmpeg.exe: FALTA")

print("\nConcluido!")
