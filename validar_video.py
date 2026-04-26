"""
Valida o vídeo gerado e mostra informações
"""
import cv2
import os

arquivo = "cortes/corte_0.mp4"

if os.path.exists(arquivo):
    tamanho = os.path.getsize(arquivo) / (1024*1024)
    
    cap = cv2.VideoCapture(arquivo)
    
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duracao = frames / fps
        
        print("=" * 70)
        print("✅ VÍDEO VALIDADO COM SUCESSO!")
        print("=" * 70)
        print(f"📁 Arquivo: {arquivo}")
        print(f"📦 Tamanho: {tamanho:.1f} MB")
        print(f"📹 Resolução: {w}x{h}")
        print(f"⏱️  Duração: {duracao:.1f}s ({frames} frames)")
        print(f"🎬 FPS: {fps}")
        print("=" * 70)
        print("\n✨ TESTE REALIZADO COM SUCESSO!")
        print("Se a legenda não aparecer no Media Player, use VLC Player")
        print("Download: https://www.videolan.org/vlc/")
        
        cap.release()
    else:
        print("❌ Vídeo corrompido")
else:
    print("❌ Arquivo não encontrado")
