import os
import sys
import subprocess
import requests
import shutil
from google import genai

# Configuração
DIRS_TO_CHECK = ["temp_upload", "cortes"]
REQUIRED_TOOLS = ["ffmpeg.exe", "ffprobe.exe"]
API_KEY = "AIzaSyCK_sCDcEPy0Kg8ldI1JcSbuCxF3_wmCxw" # Hardcoded for check based on automacao_gemini.py

print("="*60)
print("DIAGNÓSTICO GERAL - VIRALCUT PRO")
print("="*60)

# 1. Checagem de Diretórios e Permissões
print("\n[1] Verificando Sistema de Arquivos...")
all_dirs_ok = True
for d in DIRS_TO_CHECK:
    if not os.path.exists(d):
        try:
            os.makedirs(d)
            print(f"  [FIX] Diretório criado: {d}")
        except Exception as e:
            print(f"  [ERRO] Falha ao criar {d}: {e}")
            all_dirs_ok = False
    else:
        # Testar permissão de escrita
        try:
            test_file = os.path.join(d, "test_write.tmp")
            with open(test_file, "w") as f: f.write("ok")
            os.remove(test_file)
            print(f"  [OK] Diretório acessível: {d}")
        except Exception as e:
            print(f"  [ERRO] Sem permissão de escrita em {d}: {e}")
            all_dirs_ok = False

# 2. Checagem de FFmpeg
print("\n[2] Verificando FFmpeg...")
ffmpeg_ok = True
for tool in REQUIRED_TOOLS:
    path = shutil.which(tool) or os.path.abspath(tool)
    if os.path.exists(path):
        print(f"  [OK] {tool} encontrado em: {path}")
    else:
        print(f"  [ERRO CRÍTICO] {tool} NÃO encontrado! O sistema não funcionará.")
        ffmpeg_ok = False

# 3. Checagem de Conectividade (Internet)
print("\n[3] Verificando Conectividade...")
try:
    requests.get("https://www.google.com", timeout=5)
    print("  [OK] Internet conectada.")
except:
    print("  [ERRO] Sem conexão com a internet.")

# 4. Checagem de API Gemini
print("\n[4] Verificando API Google Gemini...")
try:
    client = genai.Client(api_key=API_KEY)
    # Teste leve
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Responda APENAS 'OK' se estiver me ouvindo."
    )
    if "OK" in response.text.upper():
        print("  [OK] API Gemini respondendo corretamente.")
    else:
        print(f"  [ALERTA] API respondeu algo inesperado: {response.text}")
except Exception as e:
    print(f"  [ERRO] Falha na conexão com API Gemini: {e}")

# 5. Dependências Python (Check básico)
print("\n[5] Verificando Bibliotecas Críticas...")
libs = ["flask", "yt_dlp", "cv2", "PIL", "whisper", "moviepy"]
for lib in libs:
    try:
        __import__(lib)
        print(f"  [OK] Biblioteca '{lib}' instalada.")
    except ImportError:
        # Alguns nomes de import diferem do pip install (opencv-python -> cv2, Pillow -> PIL)
        print(f"  [AVISO] Biblioteca pode estar faltando ou ter nome diferente: {lib}")

print("\n"+"="*60)
print("RELATÓRIO FINAL")
if all_dirs_ok and ffmpeg_ok:
    print("SISTEMA OPERACIONAL: OK ✅")
else:
    print("SISTEMA COM ERROS CRÍTICOS ❌")
print("="*60)
