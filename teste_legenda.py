"""
Script de teste RÁPIDO para validar se as legendas estão funcionando
"""
from motor import fabricar_corte_premium
import os

print("=" * 60)
print("TESTE DE LEGENDA - VÍDEO CURTO (5 segundos)")
print("=" * 60)

video_teste = "estoque/teste.mp4"

if not os.path.exists(video_teste):
    print(f"❌ Vídeo não encontrado: {video_teste}")
    print(f"Arquivos disponíveis em estoque/:")
    if os.path.exists("estoque"):
        print(os.listdir("estoque"))
else:
    print(f"\n[OK] Vídeo encontrado: {video_teste}")
    
    # Teste COM LEGENDA - vídeo muito curto (0-5s)
    print("\n" + "=" * 60)
    print("CRIANDO TESTE COM LEGENDA...")
    print("=" * 60)
    
    fabricar_corte_premium(
        video_teste,
        inicio=0,  # começa do início
        fim=5,     # apenas 5 segundos
        cor_hex="#00FF41",
        legenda_falada="TESTE DE LEGENDA EXTENSA PARA VERIFICAR SE A QUEBRA DE LINHA ESTÁ FUNCIONANDO CORRETAMENTE EM PIXELS"
    )
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO!")
    print("=" * 60)
    print("\n📹 Abra este arquivo para verificar:")
    print("   cortes/corte_0.mp4")
    print("\n💡 Se a legenda aparecer, o sistema está funcionando!")
