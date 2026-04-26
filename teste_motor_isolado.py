from motor import fabricar_corte_premium
import os

# Caminho do video de teste
video_path = os.path.join("temp_upload", "YTDown.com_YouTube_Como-Ser-RESPEITADO-8-Habilidades-Essenc_Media_uNAoLB9RXl0_001_1080p.mp4")

if not os.path.exists(video_path):
    print("Video de teste nao encontrado!")
    exit(1)

print(f"Testando com: {video_path}")

# Teste 1: Formato 9:16 com Fallback de Legenda
print("\n=== TESTE VERIFICAÇÃO 9:16 + LEGENDAS ===")
fabricar_corte_premium(
    video_path=video_path,
    inicio=60,
    fim=70,
    estilo="KARAOKE",
    formato="9:16",
    cor_destaque="#00FF41",
    legenda_falada="Esta é uma legenda de teste para verificar o fallback do sistema caso o Whisper não funcione corretamente.",
    output_dir="debug_cortes"
)

print("\nVerifique a pasta 'debug_cortes' para o resultado.")
