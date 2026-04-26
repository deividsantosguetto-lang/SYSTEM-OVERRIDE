import requests
import time
import json

# URL do servidor local
BASE_URL = "http://localhost:5000"

# Link do YouTube para processar
# Usando um video curto de teste
VIDEO_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - primeiro video do YouTube (18 segundos)

print("=" * 60)
print("TESTE AUTOMATIZADO - VIRALCUT PRO")
print("=" * 60)
print(f"\nProcessando video: {VIDEO_URL}")
print("Aguarde...\n")

# Fazer requisição POST para processar o vídeo
data = {
    'url': VIDEO_URL,
    'estilo': 'KARAOKE',
    'qtd_cortes': 2,  # Apenas 2 cortes para teste rápido
    'duracao': 'AUTO'
}

try:
    print("[1/3] Enviando requisicao para o servidor...")
    response = requests.post(f"{BASE_URL}/youtube", data=data, timeout=300)
    
    print(f"[2/3] Status da resposta: {response.status_code}")
    
    if response.status_code == 200:
        resultado = response.json()
        print(f"[3/3] Processamento: {resultado.get('status', 'desconhecido')}")
        
        if resultado.get('status') == 'sucesso':
            print("\n" + "=" * 60)
            print("SUCESSO! CORTES GERADOS:")
            print("=" * 60)
            
            cortes = resultado.get('cortes', [])
            for i, corte in enumerate(cortes, 1):
                print(f"\nCORTE #{i}:")
                print(f"  Titulo: {corte.get('titulo', 'N/A')}")
                print(f"  Arquivo: {corte.get('arquivo', 'N/A')}")
                print(f"  Score Viral: {corte.get('score', 'N/A')}%")
                print(f"  Justificativa: {corte.get('justificativa', 'N/A')}")
            
            print("\n" + "=" * 60)
            print(f"Total de {len(cortes)} corte(s) pronto(s) em: C:\\Users\\PC\\Desktop\\ViralCut_Pro\\cortes\\")
            print("=" * 60)
        else:
            print(f"\nERRO: {resultado.get('mensagem', 'Erro desconhecido')}")
    else:
        print(f"\nERRO HTTP: {response.status_code}")
        print(f"Mensagem: {response.text}")

except requests.exceptions.Timeout:
    print("\nERRO: Timeout - O processamento demorou mais de 5 minutos")
except requests.exceptions.ConnectionError:
    print("\nERRO: Nao foi possivel conectar ao servidor")
    print("Verifique se o servidor esta rodando em http://localhost:5000")
except Exception as e:
    print(f"\nERRO INESPERADO: {e}")
    import traceback
    traceback.print_exc()
