# -*- coding: utf-8 -*-
"""
Script de Limpeza de Arquivos Temporarios
Remove arquivos .temp e outros temporarios que podem causar problemas
"""

import os
import glob
import time

print("=" * 70)
print("LIMPEZA DE ARQUIVOS TEMPORARIOS")
print("=" * 70)

# Pastas para limpar
pastas_limpeza = ['temp_upload', 'cortes']

total_removidos = 0

for pasta in pastas_limpeza:
    if not os.path.exists(pasta):
        print(f"\n[INFO] Pasta '{pasta}' nao existe")
        continue
    
    print(f"\n[LIMPEZA] Verificando pasta: {pasta}/")
    
    # Padrões de arquivos temporários
    padroes = [
        '*.temp.mp4',
        '*.temp',
        '*.part',
        '*TEMP_MPY*',
        'audio_temp_*',
    ]
    
    for padrao in padroes:
        caminho_busca = os.path.join(pasta, padrao)
        arquivos = glob.glob(caminho_busca)
        
        if arquivos:
            print(f"  [ENCONTRADO] {len(arquivos)} arquivo(s) com padrao '{padrao}'")
            
            for arquivo in arquivos:
                try:
                    tamanho = os.path.getsize(arquivo) / 1024 / 1024  # MB
                    os.remove(arquivo)
                    print(f"    [REMOVIDO] {os.path.basename(arquivo)} ({tamanho:.2f} MB)")
                    total_removidos += 1
                except Exception as e:
                    print(f"    [ERRO] Nao foi possivel remover {os.path.basename(arquivo)}: {e}")

print("\n" + "=" * 70)
print("RESULTADO DA LIMPEZA")
print("=" * 70)

if total_removidos > 0:
    print(f"\n[OK] {total_removidos} arquivo(s) temporario(s) removido(s)")
else:
    print("\n[INFO] Nenhum arquivo temporario encontrado para remover")

print("\n[INFO] Sistema pronto para novo processamento")
print("=" * 70)
