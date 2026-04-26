"""
automacao_gemini.py
OVERRIDE.AI — Sistema de extração de cortes virais (SaaS Ready - Docker/Nuvem)
"""

import os
import re
import json
import subprocess
import tempfile
from dotenv import load_dotenv
from motor_novo import encontrar_ffmpeg

# Flexibilização para ambientes Docker: ignora o erro se o arquivo físico .env não existir
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path, override=True)

try:
    from faster_whisper import WhisperModel
except ImportError:
    raise ImportError("[ERRO CRÍTICO] faster-whisper não encontrado no ambiente.")

if os.environ.get("GOOGLE_API_KEY") and os.environ.get("GEMINI_API_KEY"):
    os.environ.pop("GOOGLE_API_KEY", None)

try:
    from google import genai
    from google.genai import types as genai_types
    USE_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai_old
        USE_NEW_SDK = False
    except ImportError:
        pass

MODELOS_FALLBACK = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"]

_WHISPER_MODEL = None

def _carregar_whisper():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        # Deteção dinâmica de hardware injetada via variável de ambiente no Docker.
        # Ex: WHISPER_DEVICE=cuda para RunPod/Colab, default cpu para local.
        dispositivo = os.environ.get("WHISPER_DEVICE", "cpu").lower()
        tipo_computacao = os.environ.get("WHISPER_COMPUTE", "int8")
        
        print(f"    [WHISPER] Carregando modelo small ({dispositivo} | {tipo_computacao})...")
        try:
            _WHISPER_MODEL = WhisperModel("small", device=dispositivo, compute_type=tipo_computacao)
            print("    [WHISPER] Modelo alocado na memória global.")
        except Exception as e:
            print(f"    [AVISO] Falha ao alocar em {dispositivo}. Reduzindo para fallback de CPU: {e}")
            _WHISPER_MODEL = WhisperModel("small", device="cpu", compute_type="int8")
            
    return _WHISPER_MODEL

def carregar_chaves():
    chaves = []
    for k, v in os.environ.items():
        if k.startswith("GEMINI_API_KEY") and v.strip() and v != "CHAVE_NAO_CONFIGURADA":
            chaves.append(v.strip())
    chaves_limpas = list(set(chaves))
    print(f"    [SISTEMA] Chaves disponíveis: {len(chaves_limpas)} | Modelos fallback: {len(MODELOS_FALLBACK)}")
    return chaves_limpas if chaves_limpas else ["CHAVE_NAO_CONFIGURADA"]

CHAVES_DISPONIVEIS = carregar_chaves()

def obter_cliente(indice):
    chave = CHAVES_DISPONIVEIS[indice % len(CHAVES_DISPONIVEIS)]
    if USE_NEW_SDK:
        return genai.Client(api_key=chave)
    else:
        genai_old.configure(api_key=chave)
        return None

def obter_duracao_video(caminho):
    try:
        import cv2
        cap = cv2.VideoCapture(caminho)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        if fps > 0 and frames > 0:
            return float(frames / fps)
    except:
        pass
    try:
        _, ffprobe = encontrar_ffmpeg()
        result = subprocess.run([
            ffprobe, "-v", "quiet", "-print_format", "json",
            "-show_format", caminho
        ], capture_output=True, text=True, timeout=30)
        info = json.loads(result.stdout)
        return float(info["format"]["duration"])
    except:
        return None

def gerar_cortes_contingencia(duracao_real, qtd_cortes, duracao_maxima):
    print(f"    [SISTEMA] Contingência ativada. Extraindo {qtd_cortes} cortes algorítmicos.")
    cortes = []
    duracao_corte = min(float(duracao_maxima), 35.0)

    if not duracao_real or duracao_real < duracao_corte:
        for i in range(qtd_cortes):
            cortes.append({
                "inicio": 0.0, 
                "fim": duracao_real or duracao_corte,
                "gancho": "Corte automático",
                "texto_na_tela": "ASSISTA ATÉ O FIM",
                "titulo": f"Corte {i+1}",
                "tema": "Automatico",
                "score": 70,
                "justificativa": "Fallback de emergência",
                "legenda_falada": "Assista até o fim",
                "copy_post": "O que você acha?",
                "hashtags": "#viral"
            })
        return cortes[:qtd_cortes]

    passo = duracao_real / (qtd_cortes + 1)
    for i in range(1, qtd_cortes + 1):
        inicio = round(passo * i, 1)
        fim = round(min(inicio + duracao_corte, duracao_real), 1)
        inicio = round(max(0.0, fim - duracao_corte), 1)
        cortes.append({
            "inicio": inicio,
            "fim": fim,
            "gancho": "Momento forte",
            "texto_na_tela": "OLHA ISSO",
            "titulo": f"Corte Viral {i}",
            "tema": "Alta Retenção",
            "score": 70,
            "justificativa": "Extração matemática proporcional.",
            "legenda_falada": "Preste atenção nisso",
            "copy_post": "Deixe sua opinião nos comentários!",
            "hashtags": "#viral #cortes"
        })
    return cortes[:qtd_cortes]

def transcrever_audio(caminho_audio):
    print("    [WHISPER] Iniciando mapeamento temporal do áudio...")
    try:
        modelo = _carregar_whisper()
        segmentos, _ = modelo.transcribe(
            caminho_audio,
            beam_size=5,
            language="pt",
            vad_filter=True,
        )
        texto_mapeado = ""
        for seg in segmentos:
            texto_mapeado += f"[{seg.start:.1f}-{seg.end:.1f}] {seg.text.strip()}\n"
        palavras = len(texto_mapeado.split())
        print(f"    [WHISPER] Transcrição concluída: {palavras} palavras mapeadas.")
        return texto_mapeado
    except Exception as e:
        print(f"    [ERRO WHISPER] Falha ao transcrever: {e}")
        return ""

def analisar_video_e_obter_cortes(caminho_video, arg_qtd_ignorado=None, arg_duracao_ignorada=None):
    qtd_cortes = 4
    duracao_minima = 15.0
    duracao_maxima = 35.0

    duracao_real = obter_duracao_video(caminho_video)
    if duracao_real:
        print(f"    [IA] Duração real do vídeo: {duracao_real:.1f}s")
    else:
        duracao_real = 3600.0
        
    print(f"\n    [SISTEMA] Override ativo: Forçando {qtd_cortes} cortes ({duracao_minima}s a {duracao_maxima}s).")

    # MUDANÇA CRÍTICA: Substituição de diretório local por descritor de arquivo nativo do OS (/tmp/)
    fd, audio_temp = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    
    try:
        ffmpeg, _ = encontrar_ffmpeg()
        process = subprocess.run([
            ffmpeg, "-y", "-i", caminho_video,
            "-vn", "-ar", "16000", "-ac", "1", "-b:a", "32k",
            "-t", "3600",
            "-y", audio_temp
        ], capture_output=True, timeout=120)
        
        if process.returncode != 0:
             print(f"    [ERRO FFMPEG] FFmpeg retornou código {process.returncode}")
             raise RuntimeError("Falha na extração de áudio.")
             
        transcricao = transcrever_audio(audio_temp)

    except Exception as e:
        print(f"    [ERRO] Falha na pipeline de áudio: {e}")
        return gerar_cortes_contingencia(duracao_real, qtd_cortes, duracao_maxima)
        
    finally:
        # Garante a exclusão física do arquivo independentemente de falhas nas linhas anteriores
        if os.path.exists(audio_temp):
            try: 
                os.remove(audio_temp)
            except: 
                pass

    if not transcricao.strip():
        print("    [AVISO] Transcrição vazia. Acionando contingência.")
        return gerar_cortes_contingencia(duracao_real, qtd_cortes, duracao_maxima)

    prompt = f"""
Você é um especialista em viralização de Shorts/Reels/TikTok.
Analise a transcrição e identifique EXATAMENTE {qtd_cortes} cortes.

Regras Matemáticas OBRIGATÓRIAS:
1. Duração exata entre {duracao_minima} e {duracao_maxima} segundos.
2. Início do corte DEVE ser o momento de um gancho forte.
3. NÃO ESCREVA NENHUMA PALAVRA ALÉM DO FORMATO EXIGIDO. Sem introdução, sem marcação markdown.

Retorne EXATAMENTE {qtd_cortes} linhas, no formato estrito:
start|end|gancho forte e curto|TEXTO CURTO PARA TELA
Exemplo:
12.4|29.8|Revelação sobre dinheiro|O MAIOR SEGREDO DOS RICOS
45.1|67.3|Momento engraçado quebrou o padrão|ISSO QUEBROU A INTERNET

TRANSCRIÇÃO:
{transcricao}
"""

    texto_ia = None
    padrao_extracao = re.compile(r'(\d+(?:\.\d+)?)\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*([^|]+?)\s*\|\s*([^\r\n]+)')

    for idx_chave in range(len(CHAVES_DISPONIVEIS)):
        cliente = obter_cliente(idx_chave)
        print(f"    [IA] Calculando matriz viral (Chave {idx_chave + 1}/{len(CHAVES_DISPONIVEIS)})...")

        for modelo in MODELOS_FALLBACK:
            try:
                if USE_NEW_SDK:
                    _safety = [
                        genai_types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                        genai_types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                        genai_types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                        genai_types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                    ]
                    response = cliente.models.generate_content(
                        model=modelo,
                        contents=[prompt],
                        config=genai_types.GenerateContentConfig(
                            max_output_tokens=300,
                            temperature=0.1,
                            response_mime_type="text/plain",
                            safety_settings=_safety,
                        )
                    )
                    texto_temp = response.text
                else:
                    from google.generativeai.types import HarmCategory, HarmBlockThreshold
                    _safety = {
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                    model_obj = genai_old.GenerativeModel(modelo)
                    response = model_obj.generate_content(
                        [prompt],
                        generation_config={"max_output_tokens": 300, "temperature": 0.1, "response_mime_type": "text/plain"},
                        safety_settings=_safety,
                    )
                    texto_temp = response.text

                if texto_temp and "|" in texto_temp:
                    texto_ia = texto_temp
                    print(f"    [IA] Sucesso com {modelo}!")
                    break

            except Exception as e:
                print(f"    [ERRO IA] {modelo}: {e}")
                continue
        
        if texto_ia:
            break

    if not texto_ia:
        print("    [ERRO CRITICO] IA falhou. Usando contingência matemática.")
        return gerar_cortes_contingencia(duracao_real, qtd_cortes, duracao_maxima)

    print(f"    [DEBUG IA] Resposta bruta:\n{texto_ia.strip()}")
    cortes_validos = []
    matches = padrao_extracao.findall(texto_ia)

    for match in matches:
        try:
            inicio = float(match[0])
            fim = float(match[1])
            gancho = match[2].strip()
            texto_na_tela = match[3].strip()

            duracao = fim - inicio

            if duracao < duracao_minima:
                fim = min(inicio + duracao_maxima, duracao_real)
            elif duracao > duracao_maxima:
                fim = inicio + duracao_maxima

            if duracao_real and fim > duracao_real:
                fim = duracao_real
                inicio = max(0.0, fim - duracao_minima)

            if (fim - inicio) < 10:
                continue

            cortes_validos.append({
                "inicio": round(inicio, 1),
                "fim": round(fim, 1),
                "gancho": gancho,
                "texto_na_tela": texto_na_tela,
                "titulo": f"Corte Viral {len(cortes_validos)+1}",
                "tema": "Alta Retenção",
                "score": 98,
                "justificativa": "Extração matemática 4 campos",
                "legenda_falada": gancho,
                "copy_post": "O que você achou? Deixe nos comentários!",
                "hashtags": "#viral #cortes"
            })
        except ValueError:
            continue

    print(f"    [IA] {len(cortes_validos)} corte(s) válido(s) gerados.")

    if len(cortes_validos) < qtd_cortes:
        faltam = qtd_cortes - len(cortes_validos)
        contingencias = gerar_cortes_contingencia(duracao_real, faltam, duracao_maxima)
        cortes_validos.extend(contingencias)

    return cortes_validos[:qtd_cortes]

def analisar_video_com_ia(caminho_video, arg_qtd_ignorado=None, arg_duracao_ignorada=None):
    return analisar_video_e_obter_cortes(caminho_video)