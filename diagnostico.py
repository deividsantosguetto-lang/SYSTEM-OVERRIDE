"""
DIAGNÓSTICO COMPLETO - Identifica exatamente o que está falhando
"""
import os
import subprocess
import cv2

print("=" * 70)
print("DIAGNÓSTICO DO SISTEMA")
print("=" * 70)

# 1. Verifica FFmpeg
print("\n1️⃣  TESTANDO FFMPEG...")
try:
    resultado = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    if resultado.returncode == 0:
        print("   ✅ FFmpeg instalado e funcionando")
    else:
        print("   ❌ FFmpeg com erro")
except:
    print("   ❌ FFmpeg NÃO ENCONTRADO - Instale: choco install ffmpeg")

# 2. Verifica OpenCV
print("\n2️⃣  TESTANDO OPENCV...")
try:
    print(f"   ✅ OpenCV versão {cv2.__version__}")
except:
    print("   ❌ OpenCV não instalado")

# 3. Verifica vídeo de teste
print("\n3️⃣  TESTANDO VÍDEO DE ENTRADA...")
if os.path.exists("estoque/teste.mp4"):
    tamanho = os.path.getsize("estoque/teste.mp4") / (1024*1024)
    cap = cv2.VideoCapture("estoque/teste.mp4")
    if cap.isOpened():
        print(f"   ✅ Vídeo encontrado ({tamanho:.1f} MB)")
        print(f"      - Duração: {cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS):.1f}s")
        print(f"      - Resolução: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
        cap.release()
    else:
        print("   ❌ Vídeo não pode ser aberto")
else:
    print("   ❌ estoque/teste.mp4 NÃO ENCONTRADO")

# 4. Testa renderização COM FFMPEG DIRETO
print("\n4️⃣  TESTE DE LEGENDA COM FFMPEG...")
if os.path.exists("estoque/teste.mp4"):
    cmd = [
        "ffmpeg",
        "-i", "estoque/teste.mp4",
        "-vf", "drawtext=text='TESTE':fontfile=C\\\\:/Windows/Fonts/arial.ttf:fontsize=60:fontcolor=lime:x=(w-text_w)/2:y=h-100",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-y",
        "cortes/teste_ffmpeg.mp4"
    ]
    
    try:
        resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if resultado.returncode == 0 and os.path.exists("cortes/teste_ffmpeg.mp4"):
            tamanho = os.path.getsize("cortes/teste_ffmpeg.mp4") / (1024*1024)
            print(f"   ✅ FFMPEG FUNCIONANDO ({tamanho:.1f} MB)")
            print(f"      Arquivo: cortes/teste_ffmpeg.mp4")
            print(f"      👉 ABRA ESTE VÍDEO PARA VERIFICAR A LEGENDA!")
        else:
            print(f"   ❌ FFMPEG FALHOU")
            if resultado.stderr:
                print(f"      Erro: {resultado.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print("   ⏱️  FFMPEG demorou muito, pode estar travado")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

print("\n" + "=" * 70)
print("FIM DO DIAGNÓSTICO")
print("=" * 70)
