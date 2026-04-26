"""
Instala FFmpeg automaticamente se não tiver
"""
import subprocess
import sys
import os

print("Instalando FFmpeg...")
print("=" * 60)

# Tenta com chocolatey
try:
    print("Tentando instalar com Chocolatey...")
    subprocess.run(["choco", "install", "ffmpeg", "-y"], check=True)
    print("✅ FFmpeg instalado com sucesso!")
except:
    try:
        print("\nTentando com winget...")
        subprocess.run(["winget", "install", "ffmpeg"], check=True)
        print("✅ FFmpeg instalado com sucesso!")
    except:
        print("\n❌ Não consegui instalar automaticamente.")
        print("\nIntale manualmente:")
        print("  1. Abra PowerShell como ADMIN")
        print("  2. Cole: choco install ffmpeg -y")
        print("\nOu baixe em: https://ffmpeg.org/download.html")
