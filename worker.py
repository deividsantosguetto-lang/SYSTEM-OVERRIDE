import os
import redis
from rq import Worker, Queue, Connection

# Define qual fila este motor vai ouvir
listen = ['default']

# Conexão blindada com o Redis do Railway
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

if __name__ == '__main__':
    print("==================================================")
    print("[WORKER SETUP] Iniciando aquecimento do motor...")
    try:
        conn = redis.from_url(redis_url)
        with Connection(conn):
            worker = Worker(list(map(Queue, listen)))
            print("[WORKER READY] Máquina ligada e aguardando vídeos.")
            print("==================================================")
            # Inicia o loop de trabalho
            worker.work()
    except Exception as e:
        print(f"[WORKER CRITICAL ERROR] Falha na conexão com o Banco de Dados: {e}")