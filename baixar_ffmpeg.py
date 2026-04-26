"""
Download FFmpeg sem erro de SSL
"""
import urllib.request
import ssl
import zipfile
import os
import shutil

print("=" * 70)
print("BAIXANDO FFMPEG (contornando SSL)")
print("=" * 70)

# Desabilita verificação SSL
ssl._create_default_https_context = ssl._create_unverified_context

url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl-shared.zip"
zip_path = "ffmpeg_download.zip"
extract_dir = "ffmpeg_extracted"

try:
    print("\n📥 Baixando FFmpeg (pode levar alguns minutos)...")
    urllib.request.urlretrieve(url, zip_path)
    print("✅ Download concluído!")
    
    print("\n📦 Extraindo...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("✅ Extração concluída!")
    
    # Encontra ffmpeg.exe
    ffmpeg_exe = None
    for root, dirs, files in os.walk(extract_dir):
        if "ffmpeg.exe" in files:
            ffmpeg_exe = os.path.join(root, "ffmpeg.exe")
            break
    
    if ffmpeg_exe:
        # Copia para pasta local
        os.makedirs("ffmpeg_local/bin", exist_ok=True)
        shutil.copy(ffmpeg_exe, "ffmpeg_local/bin/ffmpeg.exe")
        print(f"✅ FFmpeg copiado para: ffmpeg_local/bin/ffmpeg.exe")
        
        # Limpa arquivos temporários
        os.remove(zip_path)
        shutil.rmtree(extract_dir)
        
        print("\n" + "=" * 70)
        print("✅ FFMPEG INSTALADO COM SUCESSO!")
        print("=" * 70)
        print("\nAgora rode:")
        print("  python main.py")
    else:
        print("❌ FFmpeg.exe não encontrado")
        
except Exception as e:
    print(f"❌ Erro: {e}")
