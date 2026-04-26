"""
tasks.py - Jobs assíncronos para a fila
OVERRIDE.AI / ViralCut Pro (VERSÃO ATUALIZADA 2026)
Ponte de Variáveis: Texto Gigante + Gancho + Karaoke + Download Desbloqueado
"""

import os
import re
import uuid
import subprocess as _sp

from motor_novo import fabricar_corte_premium, fabricar_corte_reacao
from automacao_gemini import analisar_video_e_obter_cortes

def _sanitizar_caminho(caminho: str) -> str:
    return re.sub(r'_{2,}', '_', caminho)

def processar_arquivo(video_path, qtd_cortes, duracao, estilo, cor):
    video_path = _sanitizar_caminho(video_path)
    print(f"\n--- [JOB] INICIANDO ---")
    print(f"    Arquivo : {video_path}")
    print(f"    Cortes  : {qtd_cortes} | Duração: {duracao}s | Estilo: {estilo}")

    try:
        cortes_sugeridos = analisar_video_e_obter_cortes(video_path, qtd_cortes, duracao)

        if not cortes_sugeridos:
            raise Exception("A IA não identificou cortes válidos.")

        arquivos_gerados = []
        for corte in cortes_sugeridos:
            caminho = fabricar_corte_premium(
                video_path     = video_path,
                inicio         = corte["inicio"],
                fim            = corte["fim"],
                estilo         = estilo,
                cor_destaque   = cor,
                legenda_falada = corte.get("legenda_falada", ""),
                texto_na_tela  = corte.get("texto_na_tela", ""),
                gancho         = corte.get("gancho", ""),
                output_dir     = "cortes",
            )

            if caminho is not None and os.path.exists(caminho):
                tamanho = os.path.getsize(caminho)
                if tamanho < 1 * 1024 * 1024:
                    print(f"    [JOB] Corte ignorado (muito pequeno): {os.path.basename(caminho)}")
                    continue

                arquivos_gerados.append({
                    "arquivo":       os.path.basename(caminho),
                    "titulo":        corte.get("titulo", "Corte Viral"),
                    "duracao":       round(corte["fim"] - corte["inicio"], 1),
                    "score":         corte.get("score", 98),
                    "justificativa": corte.get("justificativa", ""),
                    "texto_na_tela": corte.get("texto_na_tela", ""),
                    "gancho":        corte.get("gancho", ""),
                    "download_url":  f"/download/{os.path.basename(caminho)}",
                })

        print(f"--- [JOB] CONCLUÍDO — {len(arquivos_gerados)} corte(s) gerado(s) ---")
        return {"status": "ok", "cortes": arquivos_gerados}

    finally:
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except:
                pass

def processar_reacao(fonte_path, reacao_path, duracao, orientacao, estilo, cor):
    print(f"\n--- [JOB REACAO] INICIANDO ---")
    print(f"    Fonte   : {fonte_path}")
    print(f"    Reação  : {reacao_path}")

    try:
        cortes_sugeridos = analisar_video_e_obter_cortes(fonte_path, 1, duracao)
        if not cortes_sugeridos:
            raise Exception("Nenhum corte identificado no vídeo fonte.")

        corte = cortes_sugeridos[0]

        clip_9_16 = fabricar_corte_premium(
            video_path     = fonte_path,
            inicio         = corte["inicio"],
            fim            = corte["fim"],
            estilo         = estilo,
            cor_destaque   = cor,
            legenda_falada = corte.get("legenda_falada", ""),
            texto_na_tela  = corte.get("texto_na_tela", ""),
            gancho         = corte.get("gancho", ""),
            output_dir     = "cortes",
        )

        if not clip_9_16 or not os.path.exists(clip_9_16):
            raise Exception("Falha ao gerar clip 9:16.")

        caminho_final = fabricar_corte_reacao(
            clip_path=clip_9_16,
            reacao_path=reacao_path,
            output_dir="cortes",
            orientacao=orientacao,
        )

        if not caminho_final or not os.path.exists(caminho_final):
            raise Exception("Falha ao montar tela dividida.")

        print(f"--- [JOB REACAO] CONCLUÍDO ---")
        return {
            "status": "ok",
            "cortes": [{
                "arquivo":       os.path.basename(caminho_final),
                "titulo":        "Modo Reação",
                "duracao":       round(corte["fim"] - corte["inicio"], 1),
                "score":         corte.get("score", 0),
                "justificativa": corte.get("justificativa", ""),
                "texto_na_tela": corte.get("texto_na_tela", ""),
                "gancho":        corte.get("gancho", ""),
                "download_url":  f"/download/{os.path.basename(caminho_final)}",
            }],
        }

    finally:
        for p in [fonte_path, reacao_path]:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass

def _is_twitch_url(url: str) -> bool:
    return "twitch.tv" in url.lower()

def _obter_duracao_youtube(url: str) -> int | None:
    try:
        r = _sp.run(
            ["yt-dlp", "--no-download", "--print", "%(duration)s",
             "--no-warnings", "--no-playlist", url],
            capture_output=True, text=True, timeout=30
        )
        txt = (r.stdout.strip().splitlines() or [""])[0]
        if txt and txt not in ("NA", "None", ""):
            return int(float(txt))
    except:
        pass
    return None

def processar_youtube(url, qtd_cortes, duracao, estilo, cor):
    from motor_novo import encontrar_ffmpeg

    is_twitch = _is_twitch_url(url)
    plataforma = "TWITCH" if is_twitch else "YOUTUBE"

    print(f"\n--- [JOB {plataforma}] INICIANDO ---")
    print(f"    URL: {url}")

    os.makedirs("temp_upload", exist_ok=True)

    for _f in os.listdir("temp_upload"):
        try:
            os.remove(os.path.join("temp_upload", _f))
        except:
            pass

    destino = f"temp_upload/vid_{uuid.uuid4().hex[:8]}.mp4"
    secao_args = []

    duracao_yt = _obter_duracao_youtube(url)
    if duracao_yt and duracao_yt > 3600:
        secao_args = ["--download-sections", "*0-3600"]

    print("    [YT-DLP] Iniciando extração (Log de velocidade aberto)...")
    
    try:
        ffmpeg_exe, _ = encontrar_ffmpeg()
        ffmpeg_dir = os.path.dirname(ffmpeg_exe)
    except:
        ffmpeg_dir = ""

    cmd_yt = [
        "yt-dlp",
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", destino,
        "--no-playlist",
    ]
    
    if ffmpeg_dir:
        cmd_yt.extend(["--ffmpeg-location", ffmpeg_dir])
        
    cmd_yt.extend(secao_args)
    cmd_yt.append(url)

    r = _sp.run(cmd_yt, timeout=1200)

    if r.returncode != 0 or not os.path.exists(destino):
        raise Exception(f"Falha no download ({plataforma}). Analise o log de erro do yt-dlp acima.")

    return processar_arquivo(destino, qtd_cortes, duracao, estilo, cor)