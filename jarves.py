"""
jarves.py - Notificações automáticas via Telegram (@jarves_oficial_bot)
Arquitetura: Fila não-bloqueante, Auto-Routing e Trava Anti-Spam (3h)
"""

import os
import re
import random
import json
import time
import threading
import urllib.request
import urllib.error
from datetime import datetime, timedelta

try:
    import requests as _requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BASE_DIR  = os.path.dirname(os.path.abspath(__file__))

CRIADORES_KEYWORDS = {
    "victor":   {"nome": "Victor (Marçal)",     "chat_id": 8454582577},
    "marcal":   {"nome": "Victor (Marçal)",     "chat_id": 8454582577},
    "josias":   {"nome": "Victor (Marçal)",     "chat_id": 8454582577},
    "yara":     {"nome": "Yara (Ruyter)",       "chat_id": 8179612951},
    "ruyter":   {"nome": "Yara (Ruyter)",       "chat_id": 8179612951},
    "davi":     {"nome": "Davi (Finch)",        "chat_id": 8122233317},
    "finch":    {"nome": "Davi (Finch)",        "chat_id": 8122233317},
    "israel":   {"nome": "Israel (Primo Rico)", "chat_id": 8745485931},
    "primoric": {"nome": "Israel (Primo Rico)", "chat_id": 8745485931},
    "primo":    {"nome": "Israel (Primo Rico)", "chat_id": 8745485931},
    "eduarda":  {"nome": "Eduarda (João Curry)", "chat_id": 7971762004},
    "joaocurry":{"nome": "Eduarda (João Curry)", "chat_id": 7971762004},
    "curry":    {"nome": "Eduarda (João Curry)", "chat_id": 7971762004},
    "john":     {"nome": "John (Renato Cariani)", "chat_id": 1613933022},
    "cariani":  {"nome": "John (Renato Cariani)", "chat_id": 1613933022},
    "renato":   {"nome": "John (Renato Cariani)", "chat_id": 1613933022},
}

criador_por_display = {**CRIADORES_KEYWORDS}

ROTEAMENTO_EQUIPE = {
    "pablo_marcal":  8454582577,
    "ruyter":        8179612951,
    "thiago_finch":  8122233317,
    "primo_rico":    8745485931,
    "joao_curry":    7971762004,
    "renato_cariani":1613933022,
}

PLATAFORMAS   = ["TikTok", "Instagram Reels", "YouTube Shorts", "Kwai"]
LOGS_FILE     = os.path.join("logs", "postagens.json")

def _strip_formatting(texto: str) -> str:
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = re.sub(r"[*_`\[\]()~>#+=|{}.!\\-]", "", texto)
    return texto.strip()

def _tg(method: str, payload: dict, sock_timeout: int = 15) -> dict:
    if not BOT_TOKEN:
        return {}
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    def _post(p: dict):
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=sock_timeout) as resp:
            return json.loads(resp.read())

    try:
        return _post(payload)
    except urllib.error.HTTPError as e:
        if e.code == 400:
            fallback = dict(payload)
            for campo in ("text", "caption"):
                if campo in fallback:
                    fallback[campo] = _strip_formatting(fallback[campo])
            fallback.pop("parse_mode", None)
            try:
                return _post(fallback)
            except:
                return {}
        return {}
    except:
        return {}

def enviar_mensagem(chat_id: int, texto: str) -> bool:
    res = _tg("sendMessage", {"chat_id": chat_id, "text": texto, "parse_mode": "HTML"})
    return bool(res.get("ok"))

def enviar_video(chat_id: int, caminho: str, caption: str = "") -> bool:
    if not BOT_TOKEN or not os.path.exists(caminho):
        return False

    tamanho = os.path.getsize(caminho)
    if tamanho > 49 * 1024 * 1024:
        return enviar_mensagem(chat_id, f"⚠️ Arquivo muito grande ({tamanho/(1024*1024):.1f} MB). Baixe manualmente.")

    if not _HAS_REQUESTS:
        return enviar_mensagem(chat_id, f"✅ Arquivo pronto: <code>{os.path.basename(caminho)}</code>")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    try:
        with open(caminho, "rb") as f:
            resp = _requests.post(
                url,
                data={"chat_id": chat_id, "caption": caption, "parse_mode": "HTML", "supports_streaming": "true"},
                files={"video": (os.path.basename(caminho), f, "video/mp4")},
                timeout=120,
            )
        return bool(resp.json().get("ok"))
    except:
        return False

def detectar_criador(nome: str) -> dict:
    clean = nome.lower().replace(" ", "").replace("-", "").replace("_", "")
    for chave, info in CRIADORES_KEYWORDS.items():
        if chave in clean:
            return info
    return {}

def _ler_logs() -> dict:
    os.makedirs("logs", exist_ok=True)
    if os.path.exists(LOGS_FILE):
        try:
            with open(LOGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def _gravar_logs(dados: dict):
    os.makedirs("logs", exist_ok=True)
    with open(LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def notificar_criador(result: dict, projeto: str, criador_info: dict = None):
    info = criador_info or detectar_criador(projeto)
    if not info:
        return

    nome = info["nome"]
    chat_id = info["chat_id"]

    chave = projeto.lower().replace(" ", "_").replace("-", "_")
    for kw, dest in ROTEAMENTO_EQUIPE.items():
        if kw in chave or kw in nome.lower():
            chat_id = int(dest)
            break

    cortes = result.get("cortes", [])
    if not cortes:
        return

    qtd = len(cortes)
    linhas = [f"📲 <b>CORTES PRONTOS - {nome}</b>\n✅ {qtd} cortes virais gerados!\n"]

    for i, corte in enumerate(cortes, 1):
        arq = corte.get("arquivo", f"corte_{i}.mp4")
        texto_gigante = corte.get("texto_na_tela", "").strip() or corte.get("gancho", "")
        gancho = corte.get("gancho", "")
        copy = corte.get("copy_post", "O que você achou?")

        linhas.append(f"🎬 <b>Corte {i}:</b> <code>{arq}</code>")
        if texto_gigante:
            linhas.append(f"🔥 <b>Texto gigante (primeiros 3s):</b> <code>{texto_gigante}</code>")
        if gancho:
            linhas.append(f"📌 Gancho: {gancho}")
        linhas.append(f"✍️ Legenda sugerida: {copy}")
        linhas.append("")

    linhas.append("Quando postar, responda exatamente assim:")
    linhas.append("<code>POSTADO TikTok 12h30</code>")

    enviar_mensagem(chat_id, "\n".join(linhas))

    for corte in cortes:
        arq = corte.get("arquivo", "")
        if not arq:
            continue
        caminho = os.path.join(BASE_DIR, "cortes", arq) if not os.path.isabs(arq) else arq
        
        texto_gigante = corte.get("texto_na_tela", "") or corte.get("gancho", "")
        caption = f"{texto_gigante}\n\n{corte.get('copy_post', '')}\n{corte.get('hashtags', '#viral #cortes')}".strip()
        
        print(f"[JARVES] Enviando vídeo → {nome}: {arq}")
        enviar_video(chat_id, caminho, caption)

    logs = _ler_logs()
    job_id = f"{projeto}_{int(time.time())}"
    logs[job_id] = {
        "criador": nome,
        "chat_id": chat_id,
        "projeto": projeto,
        "arquivos": [c.get("arquivo") for c in cortes],
        "iniciado_em": datetime.now().isoformat(),
        "confirmacoes": {},
        "lembrete_enviado": False,
        "ultimo_lembrete": None,
        "completo": False,
    }
    _gravar_logs(logs)
    print(f"[JARVES] Notificação enviada com sucesso para {nome}")

def _verificar_lembretes():
    logs = _ler_logs()
    dirty = False
    for job_id, job in list(logs.items()):
        if job.get("lembrete_enviado") or job.get("completo"):
            continue
        try:
            iniciado = datetime.fromisoformat(job.get("iniciado_em"))
            if datetime.now() - iniciado < timedelta(hours=3):
                continue
        except:
            continue

        chat_id = job.get("chat_id")
        nome = job.get("criador", "?")
        enviar_mensagem(
            chat_id,
            f"⚠️ <b>{nome}</b>, você ainda tem cortes pendentes!\n"
            f"Não esqueça de responder <code>POSTADO [plataforma]</code> quando terminar."
        )
        job["lembrete_enviado"] = True
        job["ultimo_lembrete"] = datetime.now().isoformat()
        dirty = True

    if dirty:
        _gravar_logs(logs)

# --- COMANDOS DO SISTEMA ---
OWNER_ID   = 7971762004
API_BASE   = "http://127.0.0.1:8000"
_SCALE_ORDER = ["marcal", "ruyter", "finch", "primoric", "curry", "cariani"]

def _resolve_criador_kw(kw: str) -> str:
    info = CRIADORES_KEYWORDS.get(kw.lower().strip())
    return info["nome"] if info else ""

def _parse_int(val: str, default: int, lo: int, hi: int) -> int:
    try:
        return max(lo, min(hi, int(val)))
    except (ValueError, TypeError):
        return default

def _milestones_check(linha: str, vistos: set, chat_id: int) -> None:
    MILESTONES = [
        ("YT-DLP] Baixando",           "Baixando video do YouTube..."),
        ("[IA] Duração real",          "Fazendo upload e lendo transcrição..."),
        ("[IA] Calculando matriz",      "IA desenhando ganchos virais..."),
        ("[IA] Sucesso com",            "Análise Concluída!"),
        ("[MOTOR] Gerando",             "Motor gráfico iniciado..."),
        ("[MOTOR] Renderizando Auto",   "Processando Gimbal e Textos 3D..."),
        ("[OK] Corte salvo",            "Corte finalizado com sucesso!"),
        ("JOB] CONCLUÍDO",              "Job entregue."),
    ]
    for chave, msg in MILESTONES:
        if chave in linha and chave not in vistos:
            vistos.add(chave)
            enviar_mensagem(chat_id, msg)
            return

def _acompanhar_job(job_id: str, chat_id: int) -> None:
    if not _HAS_REQUESTS: return
    try:
        url  = f"{API_BASE}/logs/{job_id}"
        resp = _requests.get(url, stream=True, timeout=900)
        vistos: set = set()
        for raw in resp.iter_lines(decode_unicode=True):
            if not raw or not raw.startswith("data:"): continue
            txt = raw[5:].strip()
            if txt.startswith("[DONE]"):
                break
            elif txt.startswith("[ERROR]"):
                enviar_mensagem(chat_id, f"Erro: {txt[7:]}")
                break
            else:
                _milestones_check(txt, vistos, chat_id)
    except:
        pass

def _cmd_gerar(chat_id: int, args: list) -> None:
    if not args:
        enviar_mensagem(chat_id, "/gerar [URL] [criador] [qtd] [dur]\nEx: /gerar youtu.be/xxx marcal 5 45")
        return
    url_video = args[0]
    criador_display = ""
    qtd_cortes, duracao = 3, 30
    idx = 1
    if idx < len(args) and not args[idx].lstrip("-").isdigit():
        criador_display = _resolve_criador_kw(args[idx])
        idx += 1
    if idx < len(args):
        qtd_cortes = _parse_int(args[idx], 3, 1, 10)
        idx += 1
    if idx < len(args):
        duracao = _parse_int(args[idx], 30, 15, 60)

    try:
        resp = _requests.post(
            f"{API_BASE}/youtube",
            data={"url": url_video, "qtd_cortes": qtd_cortes, "duracao": duracao, "estilo": "KARAOKE", "formato": "9:16", "criador": criador_display},
            timeout=20,
        )
        data   = resp.json()
        job_id = data.get("job_id")
        if job_id:
            enviar_mensagem(chat_id, f"Job iniciado!\nID: <code>{job_id}</code>\n{qtd_cortes} cortes de {duracao}s. Aguarde...")
            threading.Thread(target=_acompanhar_job, args=(job_id, chat_id), daemon=True).start()
    except Exception as exc:
        enviar_mensagem(chat_id, f"Erro: {exc}")

def _cmd_scale(chat_id: int, args: list) -> None:
    if not args:
        enviar_mensagem(chat_id, "/scale [URL1] ... [URL6] [qtd] [dur]\nOrdem: Marcal Ruyter Finch PricoRico Curry Cariani")
        return
    url_args   = [a for a in args if a.lower().startswith("http")]
    extra_args = [a for a in args if not a.lower().startswith("http")]
    urls       = url_args[:6]
    qtd_cortes = _parse_int(extra_args[0], 3, 1, 10) if len(extra_args) > 0 else 3
    duracao    = _parse_int(extra_args[1], 30, 15, 60) if len(extra_args) > 1 else 30

    data = {"qtd_cortes": str(qtd_cortes), "duracao": str(duracao), "estilo": "KARAOKE"}
    for i, (url_v, kw) in enumerate(zip(urls, _SCALE_ORDER), 1):
        data[f"url{i}"] = url_v
        data[f"criador{i}"] = _resolve_criador_kw(kw)
    for i in range(len(urls) + 1, 7):
        data[f"url{i}"] = ""
        data[f"criador{i}"] = ""

    try:
        resp   = _requests.post(f"{API_BASE}/scale", data=data, timeout=20)
        job_id = resp.json().get("job_id")
        if job_id:
            enviar_mensagem(chat_id, f"SCALE iniciado! {len(urls)} URLs. Job: <code>{job_id}</code>")
            threading.Thread(target=_acompanhar_job, args=(job_id, chat_id), daemon=True).start()
    except Exception as exc:
        enviar_mensagem(chat_id, f"Erro: {exc}")

def _cmd_status(chat_id: int) -> None:
    cortes_dir = os.path.join(BASE_DIR, "cortes")
    linhas     = ["<b>STATUS</b>\n"]
    if os.path.isdir(cortes_dir):
        mp4s = sorted([f for f in os.listdir(cortes_dir) if f.endswith(".mp4")], key=lambda f: os.path.getmtime(os.path.join(cortes_dir, f)), reverse=True)[:5]
        for f in mp4s:
            linhas.append(f"• <code>{f}</code> ({os.path.getsize(os.path.join(cortes_dir, f))/(1024*1024):.0f} MB)")
    enviar_mensagem(chat_id, "\n".join(linhas))

def _processar_update(update: dict) -> None:
    msg     = update.get("message", {})
    texto   = msg.get("text", "").strip()
    chat_id = msg.get("chat", {}).get("id")

    if not texto or chat_id is None:
        return

    _ids_conhecidos = {info["chat_id"] for info in criador_por_display.values()} | {OWNER_ID}
    if chat_id not in _ids_conhecidos:
        enviar_mensagem(chat_id, f"Seu ID: <code>{chat_id}</code>. Mande para o administrador.")
        return

    if chat_id == OWNER_ID and texto.startswith("/"):
        partes = texto.split()
        cmd    = partes[0].lower().split("@")[0]
        args   = partes[1:]
        if cmd == "/gerar": _cmd_gerar(chat_id, args)
        elif cmd == "/scale": _cmd_scale(chat_id, args)
        elif cmd == "/status": _cmd_status(chat_id)
        return

    if texto.upper().startswith("POSTADO"):
        partes  = texto.split(None, 2)
        plat_raw = partes[1] if len(partes) > 1 else ""
        horario  = partes[2] if len(partes) > 2 else datetime.now().strftime("%H:%M")
        plat_norm = plat_raw
        for p in PLATAFORMAS:
            if p.lower().replace(" ", "") in plat_raw.lower().replace(" ", ""):
                plat_norm = p
                break
        logs  = _ler_logs()
        dirty = False
        for job_id, job in logs.items():
            if job.get("chat_id") != chat_id or job.get("completo"): continue
            job["confirmacoes"][plat_norm] = {"horario": horario, "em": datetime.now().isoformat()}
            dirty = True
            if set(PLATAFORMAS).issubset(set(job["confirmacoes"].keys())):
                job["completo"] = True
                enviar_mensagem(chat_id, f"✅ <b>{job['criador']}</b> — Todos os cortes postados!")
            break
        if dirty: _gravar_logs(logs)

_poll_offset = 0
_poll_running = False

def iniciar_polling():
    if not BOT_TOKEN: return
    threading.Thread(target=_poll_loop, daemon=True, name="JarvesPoll").start()

def _poll_loop():
    global _poll_offset, _poll_running
    _poll_running = True
    print("[JARVES] Polling do Telegram iniciado.")
    while _poll_running:
        try:
            payload = {"timeout": 30, "allowed_updates": ["message"]}
            if _poll_offset: payload["offset"] = _poll_offset
            res = _tg("getUpdates", payload, 40)
            if res.get("ok"):
                for upd in res.get("result", []):
                    _poll_offset = max(_poll_offset, upd.get("update_id", 0) + 1)
                    _processar_update(upd)
            _verificar_lembretes()
        except:
            time.sleep(5)

def parar_polling():
    global _poll_running
    _poll_running = False