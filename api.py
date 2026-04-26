"""
api.py - Servidor FastAPI OVERRIDE.AI
/youtube + /upload  : endpoints síncronos (interface principal)
/processar/*        : endpoints assíncronos via RQ (legado)
/galeria            : galeria de projetos gerados
"""
import os
import re
import json
import shutil
import subprocess
import time
import uuid
import asyncio
import threading
import queue as _queue_mod
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from tasks import processar_arquivo, processar_youtube, processar_reacao

# Jarves — notificações Telegram (opcional: falha silenciosamente)
try:
    import jarves as _jarves
    _JARVES_OK = True
except Exception as _je:
    _jarves    = None
    _JARVES_OK = False
    print(f"[API] Jarves indisponível: {_je}")


# ---------------------------------------------------------------------------
# Log streaming por job (SSE)
# ---------------------------------------------------------------------------
_job_streams: dict[str, _queue_mod.Queue] = {}
_job_results: dict[str, dict]             = {}
_job_done:    dict[str, bool]             = {}
_job_lock     = threading.Lock()
_tl           = threading.local()   # thread-local: queue ativa por thread


class _DispatchWriter:
    """
    Substitui sys.stdout para capturar print() de cada thread de job
    e redirecionar as linhas para a fila do job correspondente.
    Continua escrevendo no stdout real também.
    """
    def __init__(self, real):
        self._real = real

    def write(self, s: str):
        self._real.write(s)
        q: _queue_mod.Queue | None = getattr(_tl, "q", None)
        if q is None:
            return
        # acumula buffer por thread para dividir em linhas completas
        buf = getattr(_tl, "buf", "") + s
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            stripped = line.strip()
            if stripped:
                try:
                    q.put_nowait(stripped)
                except Exception:
                    pass
        _tl.buf = buf

    def flush(self):
        self._real.flush()

    def __getattr__(self, name):
        return getattr(self._real, name)


def _job_start(job_id: str) -> None:
    """Registra o job e aponta o stdout desta thread para a fila do job."""
    q: _queue_mod.Queue = _queue_mod.Queue()
    with _job_lock:
        _job_streams[job_id] = q
        _job_results[job_id] = {}
        _job_done[job_id]    = False
    _tl.q   = q
    _tl.buf = ""


def _job_finish(job_id: str, result: dict) -> None:
    """Marca o job como concluído com o resultado."""
    with _job_lock:
        _job_results[job_id] = result
        _job_done[job_id]    = True
    _tl.q = None


# ---------------------------------------------------------------------------
# Autenticação por token
# ---------------------------------------------------------------------------
_bearer    = HTTPBearer(auto_error=False)
_API_TOKEN = os.getenv("API_TOKEN", "")

def verificar_token(creds: HTTPAuthorizationCredentials = Depends(_bearer)):
    if not _API_TOKEN:
        return
    if creds is None or creds.credentials != _API_TOKEN:
        raise HTTPException(401, detail="Token inválido ou ausente.")


# ---------------------------------------------------------------------------
# Constantes de pastas
# ---------------------------------------------------------------------------
_CORTES_DIR   = "cortes"
_TEMP_DIR     = "temp_upload"
_PROJETOS_DIR = "projetos"
_MAX_IDADE_S  = 172800  # 48h — cortes precisam existir para o Jarves enviar
_CHECK_CADA_S = 300
_MAX_UPLOAD_BYTES = 500 * 1024 * 1024  # 500 MB


# ---------------------------------------------------------------------------
# Cleanup automático
# ---------------------------------------------------------------------------
def _limpar_pasta(pasta: str, max_idade: int) -> None:
    if not os.path.isdir(pasta):
        return
    agora = time.time()
    for nome in os.listdir(pasta):
        caminho = os.path.join(pasta, nome)
        try:
            if os.path.isfile(caminho) and (agora - os.path.getmtime(caminho)) > max_idade:
                os.remove(caminho)
                print(f"[CLEANUP] Removido: {caminho}")
        except Exception as e:
            print(f"[CLEANUP] Erro: {e}")

async def _loop_cleanup() -> None:
    while True:
        await asyncio.sleep(_CHECK_CADA_S)
        # _limpar_pasta(_CORTES_DIR, _MAX_IDADE_S)  # DESATIVADO — cortes permanecem no disco
        _limpar_pasta(_TEMP_DIR,   _MAX_IDADE_S)


# ---------------------------------------------------------------------------
# Upload reader (500 MB limit)
# ---------------------------------------------------------------------------
async def _ler_upload(video: UploadFile) -> bytes:
    chunks, tamanho = [], 0
    while True:
        chunk = await video.read(1024 * 1024)
        if not chunk:
            break
        tamanho += len(chunk)
        if tamanho > _MAX_UPLOAD_BYTES:
            raise HTTPException(413, detail="Arquivo excede o limite de 500 MB.")
        chunks.append(chunk)
    return b"".join(chunks)


# ---------------------------------------------------------------------------
# Redis / RQ (opcional — modo assíncrono legado)
# ---------------------------------------------------------------------------
redis_conn = None
fila       = None
_redis_url = os.getenv(
    "REDIS_URL",
    "redis://{}:{}".format(
        os.getenv("REDIS_HOST", "localhost"),
        os.getenv("REDIS_PORT", "6379"),
    ),
)
try:
    import redis as _redis_lib
    from rq import Queue
    from rq.job import Job as RQJob
    redis_conn = _redis_lib.from_url(_redis_url, decode_responses=False)
    redis_conn.ping()
    fila = Queue("override_ai", connection=redis_conn, default_timeout=1800)
    print(f"[API] Redis conectado: {_redis_url} — modo assíncrono disponível")
except Exception as e:
    print(f"[API] Redis indisponível ({e}) — modo local (thread pool)")


# ---------------------------------------------------------------------------
# Local job store (fallback sem Redis)
# ---------------------------------------------------------------------------
_local_jobs: dict[str, dict] = {}
_local_jobs_lock = threading.Lock()
_executor = ThreadPoolExecutor(max_workers=4)

def _run_local_job(job_id: str, fn, *args) -> None:
    with _local_jobs_lock:
        _local_jobs[job_id]["status"] = "started"
    try:
        result = fn(*args)
        with _local_jobs_lock:
            _local_jobs[job_id].update({"status": "finished", "result": result})
    except Exception as exc:
        with _local_jobs_lock:
            _local_jobs[job_id].update({"status": "failed", "error": str(exc)[-500:]})

def _enfileirar_local(fn, *args) -> str:
    job_id = uuid.uuid4().hex
    with _local_jobs_lock:
        _local_jobs[job_id] = {"status": "queued", "result": None, "error": None}
    _executor.submit(_run_local_job, job_id, fn, *args)
    return job_id


# ---------------------------------------------------------------------------
# Helpers de galeria de projetos
# ---------------------------------------------------------------------------
def _slugify(text: str) -> str:
    """Transforma URL ou nome de arquivo em slug seguro."""
    text = re.sub(r'https?://[^\s]+', lambda m: m.group().rstrip('/').split('/')[-1], text)
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_-]+', '_', text).strip('_')
    return text[:40] or "projeto"

_FFMPEG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg.exe")
if not os.path.exists(_FFMPEG_PATH):
    _FFMPEG_PATH = "ffmpeg"  # fallback para PATH do sistema

def _extrair_thumbnail(video_path: str, thumb_path: str) -> None:
    """Extrai um frame do vídeo em 1 segundo como thumbnail JPEG."""
    try:
        subprocess.run(
            [_FFMPEG_PATH, "-y", "-i", video_path, "-ss", "00:00:01",
             "-vframes", "1", "-vf", "scale=320:-1", thumb_path],
            capture_output=True, timeout=30
        )
    except Exception:
        pass  # thumbnail é opcional

def _salvar_projeto(result: dict, fonte: str, tipo: str) -> None:
    """Cria pasta do projeto, extrai thumbnails e salva meta.json."""
    nome_slug  = _slugify(fonte)
    ts         = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_id = f"{nome_slug}_{ts}"
    projeto_dir = os.path.join(_PROJETOS_DIR, project_id)
    thumbs_dir  = os.path.join(projeto_dir, "thumbs")
    os.makedirs(thumbs_dir, exist_ok=True)

    for corte in result.get("cortes", []):
        src        = os.path.join(_CORTES_DIR, corte["arquivo"])
        thumb_nome = corte["arquivo"].replace(".mp4", ".jpg")
        _extrair_thumbnail(src, os.path.join(thumbs_dir, thumb_nome))
        corte["thumb_url"] = f"/thumb/{project_id}/{thumb_nome}"

    nome_display = nome_slug.replace("_", " ").title()
    meta = {
        "project_id": project_id,
        "nome":        nome_display,
        "fonte":       fonte,
        "tipo":        tipo,
        "criado_em":   datetime.now().isoformat(),
        "qtd_cortes":  len(result.get("cortes", [])),
        "cortes":      result.get("cortes", []),
    }
    with open(os.path.join(projeto_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    result["projeto"]    = nome_display
    result["project_id"] = project_id

def _listar_projetos() -> list[dict]:
    """Retorna lista de projetos ordenada do mais recente."""
    if not os.path.isdir(_PROJETOS_DIR):
        return []
    projetos = []
    for nome in sorted(os.listdir(_PROJETOS_DIR), reverse=True):
        meta_path = os.path.join(_PROJETOS_DIR, nome, "meta.json")
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, encoding="utf-8") as f:
                    projetos.append(json.load(f))
            except Exception:
                pass
    return projetos


# ---------------------------------------------------------------------------
# App FastAPI
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    import sys
    sys.stdout = _DispatchWriter(sys.stdout)

    os.makedirs(_CORTES_DIR,   exist_ok=True)
    os.makedirs(_TEMP_DIR,     exist_ok=True)
    os.makedirs(_PROJETOS_DIR, exist_ok=True)
    os.makedirs("logs",        exist_ok=True)
    asyncio.create_task(_loop_cleanup())
    if _JARVES_OK:
        _jarves.iniciar_polling()
    yield
    if _JARVES_OK:
        _jarves.parar_polling()
    _executor.shutdown(wait=False)

app       = FastAPI(title="OVERRIDE.AI", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------------------------
# Rotas — Interface principal
# ---------------------------------------------------------------------------
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/youtube")
async def youtube_sync(
    url:        str = Form(...),
    qtd_cortes: int = Form(5),
    duracao:    int = Form(30),
    estilo:     str = Form("KARAOKE"),
    formato:    str = Form("9:16"),
    criador:    str = Form(""),
    _: None = Depends(verificar_token),
):
    job_id = uuid.uuid4().hex[:14]
    _job_start(job_id)

    async def _run():
        loop = asyncio.get_running_loop()
        try:
            def _task():
                _job_start(job_id)
                return processar_youtube(url, qtd_cortes, duracao, estilo, "#00FF41")
            result = await loop.run_in_executor(_executor, _task)
            _salvar_projeto(result, url, "youtube")
            if _JARVES_OK:
                try:
                    criador_info = _jarves.criador_por_display(criador.strip()) if criador.strip() else None
                    _jarves.notificar_criador(result, result.get("projeto", url), criador_info or None)
                except Exception as _je:
                    print(f"[API] Jarves falhou (nao critico): {_je}")
            _job_finish(job_id, {"status": "sucesso", "result": result})
        except Exception as e:
            _job_finish(job_id, {"status": "erro", "mensagem": str(e)})

    asyncio.create_task(_run())
    return JSONResponse({"job_id": job_id})


@app.post("/upload")
async def upload_sync(
    file:       UploadFile = File(...),
    qtd_cortes: int        = Form(5),
    duracao:    int        = Form(30),
    estilo:     str        = Form("KARAOKE"),
    formato:    str        = Form("9:16"),
    _: None = Depends(verificar_token),
):
    conteudo = await _ler_upload(file)
    destino  = f"{_TEMP_DIR}/{uuid.uuid4().hex[:8]}.mp4"
    with open(destino, "wb") as f:
        f.write(conteudo)
    nome_original = file.filename or destino

    job_id = uuid.uuid4().hex[:14]
    _job_start(job_id)

    async def _run():
        loop = asyncio.get_running_loop()
        try:
            def _task():
                _job_start(job_id)
                return processar_arquivo(destino, qtd_cortes, duracao, estilo, "#00FF41")
            result = await loop.run_in_executor(_executor, _task)
            _salvar_projeto(result, nome_original, "upload")
            if _JARVES_OK:
                try:
                    _jarves.notificar_criador(result, result.get("projeto", nome_original))
                except Exception as _je:
                    print(f"[API] Jarves falhou (nao critico): {_je}")
            _job_finish(job_id, {"status": "sucesso", "result": result})
        except Exception as e:
            _job_finish(job_id, {"status": "erro", "mensagem": str(e)})

    asyncio.create_task(_run())
    return JSONResponse({"job_id": job_id})


# ---------------------------------------------------------------------------
# Modo Reação — tela dividida
# ---------------------------------------------------------------------------
@app.post("/reacao")
async def reacao_sync(
    reacao:      UploadFile = File(...),
    url:         str        = Form(""),
    video:       UploadFile = File(None),
    duracao:     int        = Form(60),
    orientacao:  str        = Form("stack"),
    estilo:      str        = Form("KARAOKE"),
    _: None = Depends(verificar_token),
):
    """
    Modo reação: clip do YouTube ou arquivo + vídeo de reação → tela dividida 9:16.
    """
    try:
        # Salva vídeo de reação
        reacao_bytes  = await _ler_upload(reacao)
        reacao_path   = f"{_TEMP_DIR}/{uuid.uuid4().hex[:8]}_reacao.mp4"
        with open(reacao_path, "wb") as f:
            f.write(reacao_bytes)

        # Obtém fonte (YouTube ou upload)
        if url and url.strip():
            import yt_dlp, os as _os
            fonte_path = f"{_TEMP_DIR}/{uuid.uuid4().hex[:8]}.mp4"
            ffmpeg_dir = _os.path.dirname(_os.path.abspath(__file__))
            ydl_opts = {
                "format": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]",
                "merge_output_format": "mp4",
                "outtmpl": fonte_path,
                "noplaylist": True,
                "quiet": True,
                "ffmpeg_location": ffmpeg_dir,
                "username": "oauth2",
                "password": "",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url.strip()])
            if not os.path.exists(fonte_path):
                raise HTTPException(400, detail="Falha no download do YouTube.")
        elif video and video.filename:
            fonte_bytes = await _ler_upload(video)
            fonte_path  = f"{_TEMP_DIR}/{uuid.uuid4().hex[:8]}_fonte.mp4"
            with open(fonte_path, "wb") as f:
                f.write(fonte_bytes)
        else:
            raise HTTPException(400, detail="Forneça uma URL do YouTube ou faça upload da fonte.")

        job_id = uuid.uuid4().hex[:14]
        _job_start(job_id)
        fonte_ref = url or (video.filename if video else "reacao")

        async def _run():
            loop = asyncio.get_running_loop()
            try:
                def _task():
                    _job_start(job_id)
                    return processar_reacao(fonte_path, reacao_path, duracao, orientacao, estilo, "#00FF41")
                result = await loop.run_in_executor(_executor, _task)
                _salvar_projeto(result, fonte_ref, "reacao")
                _job_finish(job_id, {"status": "sucesso", "result": result})
            except Exception as exc:
                _job_finish(job_id, {"status": "erro", "mensagem": str(exc)})

        asyncio.create_task(_run())
        return JSONResponse({"job_id": job_id})
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse({"status": "erro", "mensagem": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# Rotas — Galeria de projetos
# ---------------------------------------------------------------------------
@app.get("/galeria")
async def galeria(request: Request):
    return templates.TemplateResponse("galeria.html", {"request": request})

@app.get("/api/projetos")
async def api_listar_projetos():
    return JSONResponse(_listar_projetos())

@app.delete("/api/projetos/{project_id}")
async def api_deletar_projeto(project_id: str):
    # Bloqueia path traversal
    if any(c in project_id for c in ("..", "/", "\\")):
        raise HTTPException(400, detail="project_id inválido.")
    projeto_dir = os.path.join(_PROJETOS_DIR, project_id)
    if not os.path.isdir(projeto_dir):
        raise HTTPException(404, detail="Projeto não encontrado.")

    # Remove arquivos de corte da pasta cortes/
    meta_path = os.path.join(projeto_dir, "meta.json")
    if os.path.isfile(meta_path):
        try:
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
            for corte in meta.get("cortes", []):
                corte_path = os.path.join(_CORTES_DIR, corte.get("arquivo", ""))
                if corte_path and os.path.isfile(corte_path):
                    os.remove(corte_path)
        except Exception:
            pass

    shutil.rmtree(projeto_dir, ignore_errors=True)
    return JSONResponse({"status": "ok"})


# ---------------------------------------------------------------------------
# Thumbnails
# ---------------------------------------------------------------------------
@app.get("/thumb/{project_id}/{filename}")
async def thumbnail(project_id: str, filename: str):
    if ".." in project_id or ".." in filename:
        raise HTTPException(400)
    path = os.path.join(_PROJETOS_DIR, project_id, "thumbs", filename)
    if not os.path.isfile(path):
        raise HTTPException(404)
    return FileResponse(path, media_type="image/jpeg")


# ---------------------------------------------------------------------------
# Download de cortes
# ---------------------------------------------------------------------------
@app.get("/download/{filename}")
async def download(filename: str):
    path = os.path.join(_CORTES_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, detail="Arquivo não encontrado.")
    return FileResponse(path, media_type="video/mp4", filename=filename)


# ---------------------------------------------------------------------------
# Feature 3 — Modo SCALE: processa até 5 URLs em sequência
# ---------------------------------------------------------------------------
@app.post("/scale")
async def scale_sync(
    url1:     str = Form(""),
    url2:     str = Form(""),
    url3:     str = Form(""),
    url4:     str = Form(""),
    url5:     str = Form(""),
    url6:     str = Form(""),
    criador1: str = Form(""),
    criador2: str = Form(""),
    criador3: str = Form(""),
    criador4: str = Form(""),
    criador5: str = Form(""),
    criador6: str = Form(""),
    qtd_cortes: int = Form(3),
    duracao:    int = Form(30),
    estilo:     str = Form("KARAOKE"),
    _: None = Depends(verificar_token),
):
    """
    Processa até 6 URLs do YouTube/Twitch em sequência.
    Envia cortes para o responsável no Telegram ao fim de cada URL.
    """
    entradas = [
        (url1, criador1), (url2, criador2), (url3, criador3),
        (url4, criador4), (url5, criador5), (url6, criador6),
    ]
    urls_validas = [(u.strip(), c.strip()) for u, c in entradas if u.strip()]

    if not urls_validas:
        return JSONResponse(
            {"status": "erro", "mensagem": "Nenhuma URL fornecida."},
            status_code=400,
        )

    job_id = uuid.uuid4().hex[:14]
    _job_start(job_id)

    async def _run_scale():
        loop = asyncio.get_running_loop()
        resultados = []
        for url, criador_nome in urls_validas:
            try:
                def _task(u=url):
                    _job_start(job_id)
                    return processar_youtube(u, qtd_cortes, duracao, estilo, "#00FF41")
                result = await loop.run_in_executor(_executor, _task)
                _salvar_projeto(result, url, "scale")
                if _JARVES_OK:
                    try:
                        criador_info = _jarves.criador_por_display(criador_nome) if criador_nome else None
                        _jarves.notificar_criador(result, result.get("projeto", url), criador_info or None)
                    except Exception as _je:
                        print(f"[SCALE] Jarves falhou (nao critico): {_je}")
                resultados.append({"url": url, "criador": criador_nome, "status": "sucesso", "result": result})
            except Exception as exc:
                resultados.append({"url": url, "criador": criador_nome, "status": "erro", "mensagem": str(exc)})

        total_ok   = sum(1 for r in resultados if r["status"] == "sucesso")
        total_erro = len(resultados) - total_ok
        _job_finish(job_id, {
            "status": "sucesso", "total_ok": total_ok,
            "total_erro": total_erro, "resultados": resultados,
        })

    asyncio.create_task(_run_scale())
    return JSONResponse({"job_id": job_id})


# ---------------------------------------------------------------------------
# SSE — streaming de logs por job
# ---------------------------------------------------------------------------
@app.get("/logs/{job_id}")
async def logs_sse(job_id: str):
    async def _gen():
        # Heartbeat inicial para abrir a conexão imediatamente
        yield ": keep-alive\n\n"

        q = _job_streams.get(job_id)
        if q is None:
            yield "data: [ERROR] Job nao encontrado\n\n"
            return

        heartbeat = 0
        while True:
            # Drena todas as linhas disponíveis
            try:
                while True:
                    line = q.get_nowait()
                    yield f"data: {line}\n\n"
            except _queue_mod.Empty:
                pass

            if _job_done.get(job_id):
                # Drena o que sobrou após marcar done
                try:
                    while True:
                        line = q.get_nowait()
                        yield f"data: {line}\n\n"
                except _queue_mod.Empty:
                    pass
                result = _job_results.get(job_id, {})
                yield f"data: [DONE]{json.dumps(result, ensure_ascii=False)}\n\n"
                # Limpa estado após 60 s (GC leve)
                async def _gc(jid=job_id):
                    await asyncio.sleep(60)
                    _job_streams.pop(jid, None)
                    _job_results.pop(jid, None)
                    _job_done.pop(jid, None)
                asyncio.create_task(_gc())
                return

            # Heartbeat a cada ~15 s para manter conexão viva
            heartbeat += 1
            if heartbeat % 150 == 0:
                yield ": ping\n\n"

            await asyncio.sleep(0.1)

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",
            "Connection":       "keep-alive",
        },
    )


# ---------------------------------------------------------------------------
# Rotas legadas — processamento assíncrono via RQ
# ---------------------------------------------------------------------------
@app.post("/processar/youtube")
async def processar_youtube_endpoint(
    url:        str = Form(...),
    qtd_cortes: int = Form(3),
    duracao:    int = Form(60),
    estilo:     str = Form("KARAOKE"),
    cor:        str = Form("#00FF41"),
    _: None = Depends(verificar_token),
):
    if fila is not None:
        job = fila.enqueue(processar_youtube, url, qtd_cortes, duracao, estilo, cor)
        return JSONResponse({"job_id": job.id, "modo": "rq"})
    job_id = _enfileirar_local(processar_youtube, url, qtd_cortes, duracao, estilo, cor)
    return JSONResponse({"job_id": job_id, "modo": "local"})


@app.post("/processar/upload")
async def processar_upload_endpoint(
    video:      UploadFile = File(...),
    qtd_cortes: int        = Form(3),
    duracao:    int        = Form(60),
    estilo:     str        = Form("KARAOKE"),
    cor:        str        = Form("#00FF41"),
    _: None = Depends(verificar_token),
):
    conteudo = await _ler_upload(video)
    destino  = f"{_TEMP_DIR}/{uuid.uuid4().hex[:8]}.mp4"
    with open(destino, "wb") as f:
        f.write(conteudo)
    if fila is not None:
        job = fila.enqueue(processar_arquivo, destino, qtd_cortes, duracao, estilo, cor)
        return JSONResponse({"job_id": job.id, "modo": "rq"})
    job_id = _enfileirar_local(processar_arquivo, destino, qtd_cortes, duracao, estilo, cor)
    return JSONResponse({"job_id": job_id, "modo": "local"})


@app.get("/status/{job_id}")
async def status(job_id: str):
    if redis_conn is not None:
        try:
            job = RQJob.fetch(job_id, connection=redis_conn)
        except Exception:
            raise HTTPException(404, detail="Job não encontrado.")
        if job.is_finished:
            return JSONResponse({"status": "finished", "result": job.result})
        if job.is_failed:
            tb = str(job.exc_info or "erro desconhecido")
            return JSONResponse({"status": "failed", "error": tb[-500:]})
        if job.is_started:
            return JSONResponse({"status": "started"})
        return JSONResponse({"status": "queued"})

    with _local_jobs_lock:
        job = _local_jobs.get(job_id)
    if job is None:
        raise HTTPException(404, detail="Job não encontrado.")
    return JSONResponse({k: v for k, v in job.items() if v is not None or k == "status"})
