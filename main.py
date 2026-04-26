# main.py
import os
import subprocess
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict
from automacao_gemini import analisar_video_com_ia
from motor_novo import fabricar_corte_premium

app = FastAPI(title="Override.AI Engine")

tarefas: Dict[str, str] = {}

class RequisicaoCorte(BaseModel):
    url_video: str
    estilo: str = "KARAOKE"

def baixar_video_youtube(url: str, destino: str) -> str:
    for ext in [".mp4", ".f399.mp4", ".webm", ".mkv"]:
        arquivo = destino.replace(".mp4", ext) if ext != ".mp4" else destino
        if os.path.exists(arquivo):
            try: os.remove(arquivo)
            except: pass
                
    try:
        r = subprocess.run([
            "yt-dlp",
            "-f", "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best[height<=720]",
            "--merge-output-format", "mp4",
            "-o", destino,
            "--no-playlist",
            "--max-filesize", "500m",
            url
        ], capture_output=True, timeout=1200)

        if r.returncode == 0 and os.path.exists(destino): return destino
            
        r2 = subprocess.run([
            "yt-dlp",
            "-f", "worst[ext=mp4]/worst",
            "--merge-output-format", "mp4",
            "-o", destino,
            "--no-playlist",
            url
        ], capture_output=True, timeout=1200)

        if r2.returncode == 0 and os.path.exists(destino): return destino
        return None
    except Exception:
        return None

def processar_video_background(url_video: str, estilo: str, task_id: str):
    tarefas[task_id] = "baixando"
    
    # Alterado de /tmp para diretório local para evitar erro de permissão no Windows
    os.makedirs("cortes_temp", exist_ok=True)
    destino_base = f"cortes_temp/video_{task_id}.mp4"
    
    video_principal = baixar_video_youtube(url_video, destino_base)
    if not video_principal:
        tarefas[task_id] = "erro_download"
        return
        
    tarefas[task_id] = "analisando_ia"
    cortes_ia = analisar_video_com_ia(video_principal)
    if not cortes_ia:
        if os.path.exists(video_principal): os.remove(video_principal)
        tarefas[task_id] = "erro_analise"
        return

    tarefas[task_id] = "renderizando"
    caminho_final = None
    for corte in cortes_ia:
        caminho_final = fabricar_corte_premium(
            video_path=video_principal,
            inicio=corte["inicio"],
            fim=corte["fim"],
            cor_destaque="#00FF41",
            estilo=estilo,
            legenda_falada=corte.get("legenda_falada", "").strip(),
            texto_na_tela=corte.get("texto_na_tela", "").strip(),
            gancho=corte.get("gancho", "").strip(),
            output_dir="cortes_temp"
        )
        if caminho_final:
            break 
        
    if os.path.exists(video_principal):
        try: os.remove(video_principal)
        except: pass
        
    if caminho_final and os.path.exists(caminho_final):
        tarefas[task_id] = f"concluido|{caminho_final}"
    else:
        tarefas[task_id] = "erro_renderizacao"

@app.post("/gerar-cortes/")
async def gerar_cortes(req: RequisicaoCorte, background_tasks: BackgroundTasks):
    if not req.url_video or "http" not in req.url_video:
        raise HTTPException(status_code=400, detail="URL inválida.")
        
    estilos_validos = ["KARAOKE", "BOX", "PADRAO"]
    estilo_selecionado = req.estilo if req.estilo in estilos_validos else "KARAOKE"
    
    task_id = uuid.uuid4().hex[:8]
    tarefas[task_id] = "na_fila"
    background_tasks.add_task(processar_video_background, req.url_video, estilo_selecionado, task_id)
    
    return {"status": "processando", "task_id": task_id}

@app.get("/status/{task_id}")
async def verificar_status(task_id: str):
    status = tarefas.get(task_id, "nao_encontrado")
    if status.startswith("concluido|"):
        return {"status": "concluido", "download_url": f"/download/{task_id}"}
    return {"status": status}

@app.get("/download/{task_id}")
async def baixar_corte(task_id: str):
    status = tarefas.get(task_id, "")
    if status.startswith("concluido|"):
        caminho_arquivo = status.split("|")[1]
        if os.path.exists(caminho_arquivo):
            return FileResponse(path=caminho_arquivo, media_type='video/mp4', filename=f"override_{task_id}.mp4")
    raise HTTPException(status_code=404, detail="Arquivo indisponível ou processamento não concluído.")