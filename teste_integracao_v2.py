import os
import shutil
from servidor_flask import processar_video

# Configuração de Teste
VIDEO_TESTE = os.path.abspath("temp_upload/Me at the zoo.mp4")
if not os.path.exists(VIDEO_TESTE):
    print(f"ERRO: Vídeo de teste não encontrado em {VIDEO_TESTE}")
    exit(1)

print("="*50)
print("TESTE DE INTEGRAÇÃO V2 - GALERIA & FORMATOS")
print("="*50)

# 1. Testar Formato HORIZONTAL (16:9)
print("\n>>> TESTE 1: HORIZONTAL (16:9)")
try:
    # Simular chamada do endpoint
    resultado = processar_video(
        caminho_video=VIDEO_TESTE,
        estilo="KARAOKE",
        qtd_cortes=1,
        duracao="AUTO",
        formato="16:9"
    )
    
    # Validar resposta JSON
    dados = resultado.json
    if dados['status'] == 'sucesso':
        print(f"  [SUCESSO] API respondeu OK. Projeto: {dados['projeto']}")
        
        # Validar Pasta
        pasta_projeto = os.path.join("cortes", dados['projeto'])
        if os.path.isdir(pasta_projeto):
            print(f"  [SUCESSO] Pasta do projeto criada: {pasta_projeto}")
            
            # Validar Arquivo
            arquivos = os.listdir(pasta_projeto)
            mp4s = [f for f in arquivos if f.endswith(".mp4")]
            if mp4s:
                print(f"  [SUCESSO] Arquivo gerado: {mp4s[0]}")
            else:
                 print(f"  [ERRO] Nenhum MP4 na pasta!")
        else:
            print(f"  [ERRO] Pasta do projeto NÃO criada!")
    else:
        print(f"  [ERRO] API Falhou: {dados}")

except Exception as e:
    print(f"  [CRITICAL] Falha no teste: {e}")
    import traceback
    traceback.print_exc()

# 2. Testar Formato VERTICAL (9:16)
print("\n>>> TESTE 2: VERTICAL (9:16)")
try:
    resultado = processar_video(
        caminho_video=VIDEO_TESTE,
        estilo="KARAOKE",
        qtd_cortes=1,
        duracao="AUTO",
        formato="9:16"
    )
    # Apenas verificar se rodou sem erro, lógica similar acima
    if resultado.json['status'] == 'sucesso':
         print("  [SUCESSO] Vertical processado OK.")
    else:
         print("  [ERRO] Vertical falhou.")

except Exception as e:
    print(f"  [CRITICAL] Falha no teste 2: {e}")
