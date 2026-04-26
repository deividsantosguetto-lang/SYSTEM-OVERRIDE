"""
Download e configura FFmpeg localmente
"""
import os
import urllib.request
import zipfile
import shutil

print("=" * 70)
print("BAIXANDO FFMPEG...")
print("=" * 70)

ffmpeg_dir = "ffmpeg_local"
ffmpeg_exe = os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe")

if os.path.exists(ffmpeg_exe):
    print(f"✅ FFmpeg já configurado em {ffmpeg_exe}")
else:
    try:
        os.makedirs(ffmpeg_dir, exist_ok=True)
        
        print("\n📥 Baixando FFmpeg (Windows build)...")
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
        
        urllib.request.urlretrieve(url, zip_path)
        print("✅ Download concluído")
        
        print("\n📦 Extraindo...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        
        # Move os arquivos para a pasta bin
        for root, dirs, files in os.walk(ffmpeg_dir):
            if "ffmpeg.exe" in files:
                src = os.path.join(root, "ffmpeg.exe")
                bin_dir = os.path.join(ffmpeg_dir, "bin")
                os.makedirs(bin_dir, exist_ok=True)
                shutil.copy(src, os.path.join(bin_dir, "ffmpeg.exe"))
                print(f"✅ FFmpeg extraído para {bin_dir}")
                break
        
        os.remove(zip_path)
        print("\n✅ FFmpeg instalado com sucesso!")
        print(f"   Localização: {os.path.abspath(ffmpeg_exe)}")
        
    except Exception as e:
        print(f"\n❌ Erro ao baixar: {e}")
        print("\nAlternativa manual:")
        print("1. Baixe em: https://github.com/BtbN/FFmpeg-Builds/releases")
        print("2. Extraia em uma pasta")
        print("3. Coloque ffmpeg.exe em: ffmpeg_local/bin/")
