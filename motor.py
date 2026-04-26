"""
motor_novo.py - Motor de produção de cortes virais
OVERRIDE.AI / ViralCut Pro (VERSÃO ATUALIZADA 2026)
Arquitetura: Gimbal Digital + WordWrap 3s + Trava Dimensional + Isolamento de Memória Numpy
"""

import os
import re
import subprocess
import uuid
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _sanitizar_caminho(caminho: str) -> str:
    return re.sub(r'_{2,}', '_', caminho)

_CORRECOES_TRANSCRICAO = {
    "pablo marcal":   "Pablo Marçal",
    "pablo marsal":   "Pablo Marçal",
    "pabulo marcal":  "Pablo Marçal",
    "pabulo marsal":  "Pablo Marçal",
    "pablo marçal":   "Pablo Marçal",
    "pabulo":         "Pablo",
    "marsal":         "Marçal",
    "marcal":         "Marçal",
    "boas vendas":    "Boas vindas",
    "alfa dele":      "Alfaville",
    "ruiter":         "Ruyter",
    "ruyter pobel":   "Ruyter Poubel",
    "ruyter pouvel":  "Ruyter Poubel",
    "tiago finch":    "Thiago Finch",
    "primo ricco":    "Primo Rico",
    "joao jota":      "Joel Jota",
    "joel jotta":     "Joel Jota",
    "pabro":          "Pablo",
    "pabro marcal":   "Pablo Marçal",
    "ta":             "tá",
    "vo":             "vou",
    "num":            "não",
    "ce":             "você",
}

def _aplicar_correcoes(palavras: list) -> list:
    if not palavras:
        return palavras
    resultado = list(palavras)
    i = 0
    while i < len(resultado):
        if i + 2 < len(resultado):
            chave3 = " ".join(p["palavra"].lower() for p in resultado[i:i+3])
            if chave3 in _CORRECOES_TRANSCRICAO:
                corrigida = _CORRECOES_TRANSCRICAO[chave3].upper()
                partes = corrigida.split()
                duracao_total = resultado[i+2]["fim"] - resultado[i]["inicio"]
                dt = duracao_total / len(partes) if partes else duracao_total
                novos = []
                for j, parte in enumerate(partes):
                    novos.append({
                        "palavra": parte,
                        "inicio": resultado[i]["inicio"] + j * dt,
                        "fim":    resultado[i]["inicio"] + (j + 1) * dt,
                    })
                resultado[i:i+3] = novos
                i += len(novos)
                continue
        if i + 1 < len(resultado):
            chave2 = " ".join(p["palavra"].lower() for p in resultado[i:i+2])
            if chave2 in _CORRECOES_TRANSCRICAO:
                corrigida = _CORRECOES_TRANSCRICAO[chave2].upper()
                partes = corrigida.split()
                duracao_total = resultado[i+1]["fim"] - resultado[i]["inicio"]
                dt = duracao_total / len(partes) if partes else duracao_total
                novos = []
                for j, parte in enumerate(partes):
                    novos.append({
                        "palavra": parte,
                        "inicio": resultado[i]["inicio"] + j * dt,
                        "fim":    resultado[i]["inicio"] + (j + 1) * dt,
                    })
                resultado[i:i+2] = novos
                i += len(novos)
                continue
        chave1 = resultado[i]["palavra"].lower()
        if chave1 in _CORRECOES_TRANSCRICAO:
            resultado[i] = dict(resultado[i], palavra=_CORRECOES_TRANSCRICAO[chave1].upper())
        i += 1
    return resultado

_WHISPER_MODEL = None

def _carregar_whisper():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        print("    [WHISPER] Carregando faster-whisper small int8...")
        from faster_whisper import WhisperModel
        _WHISPER_MODEL = WhisperModel("small", device="cpu", compute_type="int8")
        print("    [WHISPER] Modelo carregado e em cache.")
    return _WHISPER_MODEL

def encontrar_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return "ffmpeg", "ffprobe"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    for pasta in [BASE_DIR, os.path.join(BASE_DIR, "ffmpeg_extracted"), os.path.join(BASE_DIR, "ffmpeg_extracted", "bin")]:
        ff = os.path.join(pasta, "ffmpeg.exe")
        fp = os.path.join(pasta, "ffprobe.exe")
        if os.path.exists(ff):
            ffprobe = fp if os.path.exists(fp) else "ffprobe"
            return ff, ffprobe
    raise FileNotFoundError("ffmpeg nao encontrado!")

def encontrar_fonte():
    candidatas = [
        os.path.join(BASE_DIR, "arialbd.ttf"),
        os.path.join(BASE_DIR, "arial.ttf"),
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf",
        "C:\\Windows\\Fonts\\verdanab.ttf",
    ]
    for f in candidatas:
        if os.path.exists(f):
            return f
    return None

def calcular_eixo_x_dinamico(video_path, total_frames, fps, width, height, target_w=720):
    import cv2
    if width <= target_w:
        return np.full(total_frames, width // 2)

    cap = cv2.VideoCapture(video_path)
    clf_frontal = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    clf_perfil  = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")
    clf_corpo   = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_upperbody.xml")

    cx_raw = []
    frames_raw = []
    passo_frames = max(1, int(fps))

    print("    [VISAO] Mapeando Auto-Reframe (Gimbal Digital)...")

    for i in range(0, total_frames, passo_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret: continue

        roi = frame[0:int(height * 0.85), :]
        gray = cv2.equalizeHist(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))
        faces = clf_frontal.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))
        if len(faces) == 0:
            faces = clf_perfil.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))
        if len(faces) == 0:
            faces = clf_corpo.detectMultiScale(gray, 1.1, 3, minSize=(50, 50))

        if len(faces) > 0:
            areas = [f[2]*f[3] for f in faces]
            maior = faces[np.argmax(areas)]
            cx = int(maior[0] + maior[2]//2)
            cx_raw.append(cx)
            frames_raw.append(i)

    cap.release()

    if len(cx_raw) < 2:
        print("    [VISAO] Rastreio insuficiente. Centro estático.")
        return np.full(total_frames, width // 2)

    cx_interpolado = np.interp(range(total_frames), frames_raw, cx_raw)
    janela = int(fps * 1.8)
    if janela % 2 == 0: janela += 1
    padded = np.pad(cx_interpolado, (janela//2, janela//2), mode='edge')
    smoothed = np.convolve(padded, np.ones(janela)/janela, mode='valid')

    print("    [VISAO] Trajetória de câmara dinâmica gerada.")
    return smoothed[:total_frames]

def desenhar_texto_com_contorno(draw, pos, texto, font, cor_texto, espessura=6):
    x, y = pos
    for dx in range(-espessura, espessura + 1):
        for dy in range(-espessura, espessura + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), texto, font=font, fill=(0, 0, 0))
    draw.text((x, y), texto, font=font, fill=cor_texto)

def desenhar_grupo_karaoke(draw, palavras_grupo, font, width, ty, cor_principal, cor_destaque, tempo_atual=None, tempos_palavras=None):
    texto_completo = " ".join(palavras_grupo)
    bbox_total = draw.textbbox((0, 0), texto_completo, font=font)
    tw_total = bbox_total[2] - bbox_total[0]
    tx_inicio = (width - tw_total) // 2

    x_atual = tx_inicio
    for i, palavra in enumerate(palavras_grupo):
        if tempo_atual is not None and tempos_palavras and i < len(tempos_palavras):
            t = tempos_palavras[i]
            cor = cor_destaque if t["inicio"] <= tempo_atual <= t["fim"] else cor_principal
        else:
            cor = cor_principal

        if i > 0:
            bbox_espaco = draw.textbbox((0, 0), " ", font=font)
            x_atual += bbox_espaco[2] - bbox_espaco[0]

        desenhar_texto_com_contorno(draw, (x_atual, ty), palavra, font, cor, espessura=6)

        bbox_p = draw.textbbox((0, 0), palavra, font=font)
        x_atual += bbox_p[2] - bbox_p[0]

def obter_fonte_tamanho(fonte_path, texto, largura_max, tamanho_inicial=90):
    from PIL import ImageFont, ImageDraw, Image
    tamanho = tamanho_inicial
    img_teste = Image.new("RGB", (largura_max, 200))
    draw = ImageDraw.Draw(img_teste)
    while tamanho >= 28:
        try:
            font = ImageFont.truetype(fonte_path, tamanho) if fonte_path else ImageFont.load_default()
            bbox = draw.textbbox((0, 0), texto, font=font)
            tw = bbox[2] - bbox[0]
            if tw <= largura_max:
                return font, tamanho
        except:
            pass
        tamanho -= 4
    return ImageFont.load_default(), 28

def transcrever_com_whisper(video_path):
    try:
        model = _carregar_whisper()
        ffmpeg, _ = encontrar_ffmpeg()
        temp_dir = os.path.join(BASE_DIR, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        audio_temp = os.path.join(temp_dir, f"audio_{uuid.uuid4().hex[:8]}.wav")

        subprocess.run([ffmpeg, "-y", "-i", video_path, "-vn", "-ar", "16000", "-ac", "1", audio_temp],
                       capture_output=True, timeout=120)

        print("    [WHISPER] Transcrevendo...")
        segments, _ = model.transcribe(audio_temp, language="pt", word_timestamps=True)

        palavras_com_tempo = []
        for segment in segments:
            for w in (segment.words or []):
                if w.word.strip():
                    palavras_com_tempo.append({
                        "palavra": w.word.strip().upper(),
                        "inicio": w.start,
                        "fim": w.end,
                    })

        if os.path.exists(audio_temp):
            os.remove(audio_temp)

        palavras_com_tempo = _aplicar_correcoes(palavras_com_tempo)
        print(f"    [WHISPER] {len(palavras_com_tempo)} palavras.")
        return palavras_com_tempo

    except Exception as e:
        print(f"    [WHISPER] Erro: {e}")
        return None

def adicionar_legenda_e_reframe(video_in, video_out, texto_na_tela="", gancho="", estilo="KARAOKE", cor_hex="#00FF41"):
    try:
        import cv2
        import numpy as np
        import textwrap
        from PIL import Image, ImageDraw, ImageFont

        fonte_path = encontrar_fonte()
        r_val = int(cor_hex[1:3], 16)
        g_val = int(cor_hex[3:5], 16)
        b_val = int(cor_hex[5:7], 16)

        cor_principal = (255, 255, 255)
        cor_destaque = (r_val, g_val, b_val)

        palavras_whisper = transcrever_com_whisper(video_in)

        cap = cv2.VideoCapture(video_in)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        if not fps or fps <= 0 or np.isnan(fps):
            fps = 30.0
            
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        TARGET_W, TARGET_H = 720, 1280

        array_cx = calcular_eixo_x_dinamico(video_in, total_frames, fps, width, height, TARGET_W)

        TEMPO_TEXTO_GIGANTE = 3.0

        if palavras_whisper and len(palavras_whisper) > 0:
            tamanho_grupo = 3
            grupos = []
            for i in range(0, len(palavras_whisper), tamanho_grupo):
                grupo_palavras = palavras_whisper[i:i + tamanho_grupo]
                grupos.append({
                    "palavras": [p["palavra"] for p in grupo_palavras],
                    "tempos": [{"inicio": p["inicio"], "fim": p["fim"]} for p in grupo_palavras],
                    "inicio": grupo_palavras[0]["inicio"],
                    "fim": grupo_palavras[-1]["fim"]
                })
        else:
            print("    [LEGENDA] Whisper falhou.")
            cap.release()
            return False

        for i in range(len(grupos) - 1):
            grupos[i]["fim"] = grupos[i + 1]["inicio"]

        fontes_grupos = []
        for grupo in grupos:
            texto_grupo = " ".join(grupo["palavras"])
            font, _ = obter_fonte_tamanho(fonte_path, texto_grupo, TARGET_W - 80, tamanho_inicial=85)
            fontes_grupos.append(font)

        temp_dir = os.path.join(BASE_DIR, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_id = uuid.uuid4().hex[:8]
        temp_video = os.path.join(temp_dir, f"leg_{temp_id}.mp4")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(temp_video, fourcc, fps, (TARGET_W, TARGET_H))

        if not out.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            temp_video = temp_video.replace(".mp4", ".avi")
            out = cv2.VideoWriter(temp_video, fourcc, fps, (TARGET_W, TARGET_H))
            if not out.isOpened():
                print("    [ERRO CRÍTICO] Impossível abrir o codec de vídeo do OpenCV no Windows.")
                cap.release()
                return False

        print("    [MOTOR] Renderizando Auto-Reframe + Legenda Viral...")

        fi = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cx_atual = int(array_cx[fi]) if fi < len(array_cx) else width // 2
            x_start = max(0, min(cx_atual - TARGET_W // 2, width - TARGET_W))
            
            # Isolamento forçado da memória Numpy para impedir Crash em C++
            frame_cropped = np.ascontiguousarray(frame[:, x_start:x_start + TARGET_W])

            if frame_cropped.shape[0] != TARGET_H or frame_cropped.shape[1] != TARGET_W:
                frame_cropped = cv2.resize(frame_cropped, (TARGET_W, TARGET_H))

            tempo_atual = fi / fps

            if texto_na_tela and tempo_atual <= TEMPO_TEXTO_GIGANTE:
                frame_rgb = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb.astype(np.uint8)).convert("RGB")
                draw = ImageDraw.Draw(img)

                linhas_texto = textwrap.wrap(texto_na_tela, width=14)
                linha_mais_longa = max(linhas_texto, key=len) if linhas_texto else ""
                font_grande, tam_fonte = obter_fonte_tamanho(fonte_path, linha_mais_longa, TARGET_W - 60, tamanho_inicial=110)
                
                altura_total_bloco = len(linhas_texto) * (tam_fonte + 10)
                ty_inicial = (TARGET_H - altura_total_bloco) // 2

                for idx_linha, texto_linha in enumerate(linhas_texto):
                    bbox = draw.textbbox((0, 0), texto_linha, font=font_grande)
                    largura_linha = bbox[2] - bbox[0]
                    tx = (TARGET_W - largura_linha) // 2
                    ty_linha = ty_inicial + (idx_linha * (tam_fonte + 10))
                    
                    desenhar_texto_com_contorno(draw, (tx, ty_linha), texto_linha, font_grande, (0, 255, 255), espessura=7)

                frame_out = cv2.cvtColor(np.array(img, dtype=np.uint8), cv2.COLOR_RGB2BGR)
                out.write(frame_out)

            else:
                grupo_atual = None
                font_atual = None
                tempos_atual = None

                for gi, grupo in enumerate(grupos):
                    if grupo["inicio"] <= tempo_atual <= grupo["fim"]:
                        grupo_atual = grupo["palavras"]
                        font_atual = fontes_grupos[gi]
                        tempos_atual = grupo.get("tempos")
                        break

                if grupo_atual and font_atual:
                    frame_rgb = cv2.cvtColor(frame_cropped, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb.astype(np.uint8)).convert("RGB")
                    draw = ImageDraw.Draw(img)
                    ty = int(TARGET_H * 0.78)

                    desenhar_grupo_karaoke(draw, grupo_atual, font_atual, TARGET_W, ty, cor_principal, cor_destaque, tempo_atual, tempos_atual)
                    frame_out = cv2.cvtColor(np.array(img, dtype=np.uint8), cv2.COLOR_RGB2BGR)
                    out.write(frame_out)
                else:
                    out.write(frame_cropped)

            fi += 1

        cap.release()
        out.release()

        ffmpeg, _ = encontrar_ffmpeg()
        subprocess.run([
            ffmpeg, "-y",
            "-i", temp_video,
            "-i", video_in,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "fast", "-crf", "28", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-r", "30",
            "-movflags", "+faststart",
            video_out
        ], capture_output=True, timeout=600)

        if os.path.exists(temp_video):
            os.remove(temp_video)

        return os.path.exists(video_out) and os.path.getsize(video_out) > 0

    except Exception as e:
        print(f"    [LEGENDA] Erro estrutural: {e}")
        return False

def fabricar_corte_premium(
    video_path, inicio, fim,
    estilo="KARAOKE", cor_destaque="#00FF41",
    legenda_falada="",          
    texto_na_tela="",           
    gancho="",                  
    output_dir="cortes", formato="9:16", is_premium=True
):
    video_path = _sanitizar_caminho(video_path)
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg, _ = encontrar_ffmpeg()
    duracao = fim - inicio

    if duracao <= 0:
        return None

    nome_saida = f"corte_{int(inicio)}_{estilo}_{uuid.uuid4().hex[:6]}.mp4"
    caminho_saida = os.path.join(output_dir, nome_saida)
    temp_raw = caminho_saida.replace(".mp4", "_raw.mp4")

    print(f"\n    [MOTOR] Gerando: {nome_saida} ({duracao:.1f}s)")

    subprocess.run([
        ffmpeg, "-y",
        "-ss", str(inicio), "-i", video_path, "-t", str(duracao),
        "-vf", "scale=-2:1280:flags=lanczos",
        "-c:v", "libx264", "-preset", "fast", "-crf", "28",
        "-c:a", "aac", "-b:a", "128k",
        temp_raw
    ], capture_output=True, timeout=600)

    if not os.path.exists(temp_raw) or os.path.getsize(temp_raw) == 0:
        print("    [ERRO] Falha na extração FFmpeg.")
        return None

    sucesso = adicionar_legenda_e_reframe(
        temp_raw, caminho_saida,
        texto_na_tela=texto_na_tela or legenda_falada,
        gancho=gancho,
        estilo=estilo,
        cor_hex=cor_destaque
    )

    if os.path.exists(temp_raw):
        os.remove(temp_raw)

    if sucesso and os.path.exists(caminho_saida):
        mb = os.path.getsize(caminho_saida) / (1024 * 1024)
        print(f"    [OK] Corte salvo: {caminho_saida} ({mb:.1f} MB)")
        return caminho_saida
    return None

def fabricar_corte_reacao(clip_path, reacao_path, output_dir="cortes", orientacao="stack"):
    clip_path   = _sanitizar_caminho(clip_path)
    reacao_path = _sanitizar_caminho(reacao_path)
    os.makedirs(output_dir, exist_ok=True)
    ffmpeg, _ = encontrar_ffmpeg()
    nome_saida = f"reacao_{uuid.uuid4().hex[:8]}.mp4"
    caminho_saida = os.path.join(output_dir, nome_saida)

    print(f"\n    [REACAO] Montando tela dividida ({orientacao})...")

    if orientacao == "side":
        filtro = (
            "[0:v]scale=540:1920:force_original_aspect_ratio=increase,"
            "crop=540:1920,setsar=1[left];"
            "[1:v]scale=540:1920:force_original_aspect_ratio=increase,"
            "crop=540:1920,setsar=1[right];"
            "[left][right]hstack=inputs=2[v]"
        )
    else:
        filtro = (
            "[0:v]scale=1080:960:force_original_aspect_ratio=increase,"
            "crop=1080:960,setsar=1[top];"
            "[1:v]scale=1080:960:force_original_aspect_ratio=increase,"
            "crop=1080:960,setsar=1[bot];"
            "[top][bot]vstack=inputs=2[v]"
        )

    cmd = [
        ffmpeg, "-y", "-i", clip_path, "-i", reacao_path, "-filter_complex", filtro,
        "-map", "[v]", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "fast", "-crf", "32", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-r", "30", "-shortest", "-movflags", "+faststart",
        caminho_saida,
    ]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        cmd_noaudio = [
            ffmpeg, "-y", "-i", clip_path, "-i", reacao_path, "-filter_complex", filtro,
            "-map", "[v]", "-an",
            "-c:v", "libx264", "-preset", "fast", "-crf", "32", "-pix_fmt", "yuv420p",
            "-r", "30", "-shortest", "-movflags", "+faststart", caminho_saida,
        ]
        r2 = subprocess.run(cmd_noaudio, capture_output=True, text=True, timeout=600)
        if r2.returncode != 0:
            print(f"    [REACAO ERRO] {r2.stderr[-400:]}")
            return None

    if os.path.exists(caminho_saida) and os.path.getsize(caminho_saida) > 0:
        mb = os.path.getsize(caminho_saida) / (1024 * 1024)
        print(f"    [REACAO OK] {caminho_saida} ({mb:.1f} MB)")
        return caminho_saida

    return None