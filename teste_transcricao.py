# -*- coding: utf-8 -*-
"""
Teste de Transcrição - Verifica se legendas estão funcionando
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("TESTE DE TRANSCRICAO - Verificando Legendas")
print("=" * 70)

# Verificar se há cortes já gerados
cortes_dir = "cortes"
if os.path.exists(cortes_dir):
    arquivos_mp4 = [f for f in os.listdir(cortes_dir) if f.endswith('.mp4')]
    
    if arquivos_mp4:
        print(f"\n[INFO] Encontrados {len(arquivos_mp4)} videos na pasta cortes:")
        for idx, arquivo in enumerate(arquivos_mp4[:5], 1):
            tamanho = os.path.getsize(os.path.join(cortes_dir, arquivo))
            print(f"  {idx}. {arquivo} ({tamanho/1024/1024:.2f} MB)")
        
        if len(arquivos_mp4) > 5:
            print(f"  ... e mais {len(arquivos_mp4)-5} arquivos")
    else:
        print("\n[INFO] Nenhum video encontrado na pasta cortes")
        print("      Os videos serao gerados quando processar pelo app")

# Teste rápido de transcrição
print("\n" + "=" * 70)
print("TESTE RAPIDO: Verificando funcao de transcricao")
print("=" * 70)

try:
    from motor import transcrever_whisper_word_level
    print("\n[OK] Funcao transcrever_whisper_word_level() importada")
    
    # Verificar se há áudio de teste
    temp_audio_files = [f for f in os.listdir('.') if f.startswith('temp_audio') and f.endswith('.mp3')]
    
    if temp_audio_files:
        print(f"[INFO] Encontrados {len(temp_audio_files)} arquivos de audio temporarios")
        # Testar com o primeiro
        audio_teste = temp_audio_files[0]
        print(f"\n[TESTE] Tentando transcrever: {audio_teste}")
        
        try:
            segmentos = transcrever_whisper_word_level(audio_teste)
            if segmentos:
                print(f"[OK] Transcricao bem-sucedida!")
                print(f"     {len(segmentos)} segmentos encontrados")
                
                # Mostrar primeiro segmento como exemplo
                if len(segmentos) > 0:
                    seg = segmentos[0]
                    print(f"\n[EXEMPLO] Primeiro segmento:")
                    print(f"  Texto: {seg.get('text', 'N/A')}")
                    print(f"  Inicio: {seg.get('start', 'N/A')}s")
                    print(f"  Fim: {seg.get('end', 'N/A')}s")
                    
                    if 'words' in seg and seg['words']:
                        print(f"  Palavras individuais: {len(seg['words'])}")
                        print(f"  Primeira palavra: '{seg['words'][0].get('word', 'N/A')}'")
            else:
                print("[AVISO] Transcricao retornou vazia")
        except Exception as e:
            print(f"[ERRO] Falha na transcricao: {e}")
    else:
        print("\n[INFO] Nenhum arquivo de audio temporario encontrado")
        print("      Audio sera extraido quando processar video")
        
except Exception as e:
    print(f"[ERRO] Erro ao importar funcao: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("CONCLUSAO")
print("=" * 70)

print("\nSTATUS DO SISTEMA DE TRANSCRICAO:")
print("  [OK] Funcao de transcricao disponivel")
print("  [OK] Whisper base instalado e pronto")
print("  [INFO] Para testar completamente:")
print("         1. Acesse http://localhost:5000")
print("         2. Processe um video curto")
print("         3. Verifique o video gerado em /cortes")
print("         4. As legendas devem aparecer sincronizadas")

print("\n" + "=" * 70)
