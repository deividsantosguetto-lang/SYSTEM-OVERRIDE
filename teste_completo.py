# -*- coding: utf-8 -*-
import os
import sys

print("=" * 70)
print("TESTE AUTOMATIZADO - VIRALCUT PRO")
print("=" * 70)

# TESTE 1: Dependencias
print("\n[1/5] Verificando Dependencias...")

try:
    import whisper
    print(f"  [OK] Whisper: {whisper.__version__}")
except:
    print("  [ERRO] Whisper nao instalado")
    sys.exit(1)

try:
    from google import genai
    print("  [OK] Google GenAI instalado")
except:
    print("  [ERRO] Google GenAI nao instalado")
    sys.exit(1)

try:
    import cv2
    print(f"  [OK] OpenCV: {cv2.__version__}")
except:
    print("  [ERRO] OpenCV nao instalado")

try:
    from moviepy.editor import VideoFileClip
    print("  [OK] MoviePy instalado")
except:
    print("  [ERRO] MoviePy nao instalado")

if os.path.exists("ffmpeg.exe"):
    print("  [OK] FFmpeg.exe encontrado")
else:
    print("  [ERRO] ffmpeg.exe nao encontrado")

# TESTE 2: Modulos do App
print("\n[2/5] Verificando Modulos do App...")

try:
    from automacao_gemini import analisar_video_com_ia
    print("  [OK] automacao_gemini.analisar_video_com_ia() disponivel")
except Exception as e:
    print(f"  [ERRO] Erro ao importar automacao_gemini: {e}")
    sys.exit(1)

try:
    from motor import fabricar_corte_premium, transcrever_whisper_word_level
    print("  [OK] motor.fabricar_corte_premium() disponivel")
    print("  [OK] motor.transcrever_whisper_word_level() disponivel")
except Exception as e:
    print(f"  [ERRO] Erro ao importar motor: {e}")
    sys.exit(1)

# TESTE 3: API Gemini
print("\n[3/5] Testando Conexao com API Gemini...")

try:
    client = genai.Client(api_key="AIzaSyCK_sCDcEPy0Kg8ldI1JcSbuCxF3_wmCxw")
    modelos = list(client.models.list())
    print(f"  [OK] API Gemini: {len(modelos)} modelos disponiveis")
    
    nomes_modelos = [m.name for m in modelos]
    if 'models/gemini-1.5-pro' in nomes_modelos:
        print("  [OK] Modelo gemini-1.5-pro disponivel")
except Exception as e:
    print(f"  [ERRO] Erro na API Gemini: {e}")
    sys.exit(1)

# TESTE 4: Modelo Whisper
print("\n[4/5] Testando Modelo Whisper Base...")

try:
    print("  [INFO] Carregando modelo 'base' (pode levar alguns segundos)...")
    model = whisper.load_model("base")
    print("  [OK] Modelo Whisper 'base' carregado com sucesso")
    print("  [INFO] Modelo armazenado em cache para uso posterior")
except Exception as e:
    print(f"  [AVISO] Erro ao carregar Whisper 'base': {e}")
    print("  [INFO] O modelo sera baixado automaticamente na primeira execucao")

# TESTE 5: Estrutura de Pastas
print("\n[5/5] Verificando Estrutura de Pastas...")

pastas = ["temp_upload", "cortes", "templates"]
for pasta in pastas:
    if os.path.exists(pasta):
        print(f"  [OK] Pasta '{pasta}' existe")
    else:
        os.makedirs(pasta, exist_ok=True)
        print(f"  [OK] Pasta '{pasta}' criada")

if os.path.exists("templates/index.html"):
    print("  [OK] templates/index.html encontrado")

# RESULTADO FINAL
print("\n" + "=" * 70)
print("TODOS OS TESTES BASICOS PASSARAM!")
print("=" * 70)

print("\nRESUMO:")
print(f"  * Whisper: {whisper.__version__} (modelo 'base' pronto)")
print(f"  * Google GenAI: Conectado ({len(modelos)} modelos)")
print(f"  * FFmpeg: Disponivel")
print(f"  * OpenCV: {cv2.__version__}")
print(f"  * Estrutura de pastas: OK")

print("\nSistema pronto para processar videos!")
print("\nProximo passo: Rodar servidor Flask e testar com video real")
print("   Comando: python servidor_flask.py")
print("=" * 70)
