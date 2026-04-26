"""
DIAGNOSTICO COMPLETO DO SERVIDOR
Este script verifica todas as dependencias e configuracoes necessarias
"""

import sys
import os

print("=" * 80)
print("DIAGNOSTICO DO SERVIDOR - VIRALCUT PRO")
print("=" * 80)
print()

# VERIFICAR PYTHON
print("[1] VERSAO DO PYTHON")
print(f"   [OK] Python {sys.version}")
print()

# VERIFICAR BIBLIOTECAS INSTALADAS
print("[2] BIBLIOTECAS NECESSARIAS")
bibliotecas = [
    ("streamlit", "streamlit"),
    ("flask", "Flask"),
    ("fastapi", "fastapi"),
    ("yt_dlp", "yt-dlp"),
    ("google.generativeai", "google-generativeai"),
    ("dotenv", "python-dotenv"),
    ("whisper", "openai-whisper"),
    ("cv2", "opencv-python"),
    ("PIL", "Pillow"),
    ("numpy", "numpy")
]

libs_faltando = []
for lib_import, lib_pip in bibliotecas:
    try:
        __import__(lib_import)
        print(f"   [OK] {lib_pip}")
    except ImportError:
        print(f"   [FALTA] {lib_pip}")
        libs_faltando.append(lib_pip)

print()

# VERIFICAR ARQUIVO .env E CHAVE API
print("[3] CONFIGURACAO DA API (arquivo .env)")

if os.path.exists(".env"):
    print("   [OK] Arquivo .env existe")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        
        if api_key and len(api_key) > 10:
            print(f"   [OK] GEMINI_API_KEY configurada ({len(api_key)} caracteres)")
        else:
            print(f"   [ERRO] GEMINI_API_KEY vazia ou invalida")
    except:
        print("   [AVISO] Nao foi possivel verificar o conteudo do .env")
else:
    print("   [ERRO] Arquivo .env NAO EXISTE")

print()

# VERIFICAR FFMPEG
print("[4] FFMPEG")

ffmpeg_local = os.path.abspath("ffmpeg.exe")
if os.path.exists(ffmpeg_local):
    tamanho_mb = os.path.getsize(ffmpeg_local) / (1024 * 1024)
    print(f"   [OK] ffmpeg.exe encontrado ({tamanho_mb:.1f} MB)")
else:
    print(f"   [ERRO] ffmpeg.exe NAO encontrado")

print()

# VERIFICAR ESTRUTURA DE PASTAS
print("[5] ESTRUTURA DE PASTAS")

pastas = ["temp_upload", "cortes", "templates"]
for pasta in pastas:
    if os.path.exists(pasta):
        print(f"   [OK] {pasta}/")
    else:
        print(f"   [AVISO] {pasta}/ nao existe (sera criada automaticamente)")

print()

# VERIFICAR ARQUIVOS DO SERVIDOR
print("[6] ARQUIVOS DO SERVIDOR")

servidores = {
    "app_web.py": "Streamlit",
    "servidor_flask.py": "Flask",
    "api.py": "FastAPI"
}

for arquivo, tipo in servidores.items():
    if os.path.exists(arquivo):
        print(f"   [OK] {arquivo} ({tipo})")
    else:
        print(f"   [ERRO] {arquivo} ({tipo}) nao encontrado")

print()

# VERIFICAR FONTE
print("[7] ARQUIVO DE FONTE")

if os.path.exists("TheBoldFont.ttf"):
    print(f"   [OK] TheBoldFont.ttf encontrada")
else:
    print(f"   [AVISO] TheBoldFont.ttf nao encontrada")

print()

# RESUMO E RECOMENDACOES
print("=" * 80)
print("RESUMO E RECOMENDACOES")
print("=" * 80)

tem_erro = False

if libs_faltando:
    tem_erro = True
    print("\n[ERRO] BIBLIOTECAS FALTANDO:")
    print("\n   Execute este comando para instalar:")
    print(f"\n   pip install {' '.join(libs_faltando)}")
    print()

if not os.path.exists(".env"):
    tem_erro = True
    print("\n[ERRO] CONFIGURAR API KEY:")
    print("\n   1. Crie um arquivo chamado '.env' na pasta do projeto")
    print("   2. Adicione a linha: GEMINI_API_KEY=sua_chave_aqui")
    print("   3. Obtenha sua chave em: https://aistudio.google.com/app/apikey")
    print()

if not os.path.exists(ffmpeg_local):
    tem_erro = True
    print("\n[ERRO] FFMPEG NAO ENCONTRADO:")
    print("\n   Execute: python baixar_ffmpeg.py")
    print()

if not tem_erro:
    print("\n[SUCESSO] Todas as dependencias estao OK!")
    print()

print("\nPARA INICIAR O SERVIDOR:")
print("\n   Opcao 1 (Streamlit): streamlit run app_web.py")
print("   Opcao 2 (Flask): python servidor_flask.py")
print("   Opcao 3 (FastAPI): uvicorn api:app --reload --host 0.0.0.0 --port 5000")
print("   Opcao 4 (Arquivo BAT): INICIAR_APP.bat")
print()

print("=" * 80)
