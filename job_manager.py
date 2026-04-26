import threading
import uuid
import time
import logging

# Dicionario global para armazenar status dos jobs
# Estrutura: { 
#   "job_id": { 
#       "status": "processing" | "completed" | "error",
#       "progress": 0,
#       "log": "Iniciando...",
#       "result": None,
#       "error_msg": None,
#       "created_at": timestamp
#   }
# }
JOBS = {}

class JobManager:
    def __init__(self):
        self.jobs = JOBS

    def start_job(self, target_func, *args, **kwargs):
        """Inicia uma tarefa em background e retorna o ID"""
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "status": "processing",
            "progress": 0,
            "log": "Na fila de processamento...",
            "result": None,
            "error_msg": None,
            "created_at": time.time()
        }
        
        # Wrapper para capturar resultado ou erro
        def thread_wrapper():
            try:
                # Injetar callback de progresso se a funcao aceitar
                # Por enquanto nao vamos complicar, apenas rodar
                print(f"[JOB {job_id}] Iniciado.")
                self.update_job(job_id, progress=10, log="Processando vídeo...")
                
                result = target_func(*args, **kwargs)
                
                # Se o resultado for um tuple (response, status), pegar so o response
                if isinstance(result, tuple):
                    result = result[0]
                    
                # Se for objeto Flask Response ou jsonify, tentar extrair json 
                # (Mas aqui target_func deve retornar dict/lista pura preferencialmente)
                if hasattr(result, 'get_json'):
                    result = result.get_json()
                elif hasattr(result, 'json'):
                    result = result.json
                
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["progress"] = 100
                self.jobs[job_id]["log"] = "Concluído com sucesso!"
                self.jobs[job_id]["result"] = result
                print(f"[JOB {job_id}] Concluido.")
                
            except Exception as e:
                print(f"[JOB {job_id}] Erro: {e}")
                import traceback
                traceback.print_exc()
                self.jobs[job_id]["status"] = "error"
                self.jobs[job_id]["error_msg"] = str(e)
                self.jobs[job_id]["log"] = f"Erro fatal: {str(e)}"

        thread = threading.Thread(target=thread_wrapper)
        thread.daemon = True # Mata a thread se o servidor cair
        thread.start()
        
        return job_id

    def get_job(self, job_id):
        return self.jobs.get(job_id)

    def update_job(self, job_id, status=None, progress=None, log=None):
        if job_id in self.jobs:
            if status: self.jobs[job_id]["status"] = status
            if progress: self.jobs[job_id]["progress"] = progress
            if log: self.jobs[job_id]["log"] = log

    def cleanup_old_jobs(self, max_age_seconds=3600):
        """Limpa jobs antigos da memoria para nao estourar RAM"""
        now = time.time()
        to_delete = []
        for jid, data in self.jobs.items():
            if now - data["created_at"] > max_age_seconds:
                to_delete.append(jid)
        for jid in to_delete:
            del self.jobs[jid]
