"""
Extrai áudio e transcreve automaticamente
"""
import subprocess
import os

print("=" * 70)
print("INSTALANDO WHISPER (transcrição de áudio)")
print("=" * 70)

# Instala whisper
print("\n📦 Instalando openai-whisper...")
resultado = subprocess.run(["pip", "install", "-q", "openai-whisper"], capture_output=True)

if resultado.returncode == 0:
    print("✅ Whisper instalado com sucesso!")
else:
    print("❌ Erro ao instalar")
    print(resultado.stderr.decode())
