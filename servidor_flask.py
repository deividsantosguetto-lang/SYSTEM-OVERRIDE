import os
import redis
from flask import Flask, render_template, request, jsonify
from rq import Queue
# Certifique-se que o tasks.py tem esta função escrita lá dentro!
from tasks import executar_processamento_youtube 

app = Flask(__name__)

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)
q = Queue('default', connection=conn)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/youtube', methods=['POST'])
def youtube():
    data = request.form
    job = q.enqueue(
        executar_processamento_youtube,
        data.get('url'),
        data.get('estilo'),
        int(data.get('qtd_cortes', 1)), # Default para 1 corte
        int(data.get('duracao', 30)), # Default para 30 segundos
        data.get('formato', '9:16'), # Default para 9:16
        job_timeout='1h'
    )
    return jsonify({"status": "success", "job_id": job.get_id()})

@app.route('/job/<job_id>')
def get_status(job_id):
    job = q.fetch_job(job_id)
    if not job: return jsonify({"status": "not_found"}), 404
    if job.is_finished: return jsonify({"status": "completed", "result": job.result})
    if job.is_failed: return jsonify({"status": "error"}), 500
    return jsonify({"status": "processing"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)