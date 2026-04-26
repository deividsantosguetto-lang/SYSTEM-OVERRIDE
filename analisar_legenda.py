"""
Verifica se a legenda foi desenhada comparando cores
"""
import cv2
import numpy as np
from PIL import Image

print("=" * 70)
print("ANÁLISE DE LEGENDA")
print("=" * 70)

# Carrega a imagem do vídeo
img = cv2.imread("debug_frames/frame_do_video.jpg")

if img is None:
    print("❌ Imagem não encontrada")
else:
    altura, largura = img.shape[:2]
    print(f"\n✓ Imagem carregada: {largura}x{altura}")
    
    # Procura por pixels verde brilhante (legenda)
    # Verde em BGR = (0, 255, 65) ou próximo
    
    # Define range de cores para verde brilhante
    lower_green = np.array([0, 200, 0])
    upper_green = np.array([100, 255, 150])
    
    # Cria máscara de pixels verdes
    mask = cv2.inRange(img, lower_green, upper_green)
    
    # Conta pixels verdes
    pixels_verdes = np.count_nonzero(mask)
    
    print(f"\n📊 Análise de cores:")
    print(f"  Pixels verdes encontrados: {pixels_verdes}")
    
    if pixels_verdes > 100:
        print(f"\n✅ LEGENDA DETECTADA! ({pixels_verdes} pixels verdes)")
        
        # Também procura por contorno preto
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([50, 50, 50])
        mask_black = cv2.inRange(img, lower_black, upper_black)
        pixels_pretos = np.count_nonzero(mask_black)
        
        if pixels_pretos > 50:
            print(f"✅ CONTORNO DETECTADO! ({pixels_pretos} pixels pretos)")
            print("\n" + "=" * 70)
            print("🎉 SUCESSO! LEGENDA FOI RENDERIZADA COM SUCESSO!")
            print("=" * 70)
        else:
            print("⚠️ Contorno não detectado (pode estar muito sutil)")
    else:
        print(f"\n❌ LEGENDA NÃO DETECTADA")
        print(f"   Pixels verdes esperados: > 100")
        print(f"   Pixels verdes encontrados: {pixels_verdes}")
        
        # Salva máscara para debug
        cv2.imwrite("debug_frames/mask_verde.jpg", mask)
        print(f"\n   Máscara salva em: debug_frames/mask_verde.jpg")
