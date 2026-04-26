"""
Instala FFmpeg do zero
"""
import subprocess
import os

print("=" * 70)
print("INSTALANDO FFMPEG")
print("=" * 70)

# Tenta winget (mais moderno)
try:
    print("\n1️⃣ Tentando com winget...")
    subprocess.run(["winget", "install", "--id", "FFmpeg.FFmpeg"], check=True)
    print("✅ FFmpeg instalado!")
except:
    # Tenta chocolatey
    try:
        print("\n2️⃣ Tentando com choco...")
        subprocess.run(["choco", "install", "ffmpeg", "-y"], check=True)
        print("✅ FFmpeg instalado!")
    except:
        print("\n❌ Não consegui instalar")
        print("\nIntale manualmente:")
        print("1. Abra PowerShell como ADMIN")
        print("2. Cole um destes comandos:")
        print("   winget install FFmpeg.FFmpeg")
        print("   OU")
        print("   choco install ffmpeg -y")
        print("\n3. Depois rode main.py de novo")
