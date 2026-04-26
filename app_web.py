from flask import Flask, render_template, request, jsonify, send_from_directory
import os, yt_dlp, time
from automacao_gemini import analisar_video_para_virais
from adicionar_legendas_v2 import processar_legendas_finais

app = Flask(__name__)
UPLOAD_FOLDER, OUTPUT_FOLDER = 'uploads', 'cortes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True); os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/youtube', methods=['POST'])
def processar_youtube():
    url, estilo = request.form.get('url'), request.form.get('estilo')
    densidade = int(request.form.get('densidade', 5))
    
    try:
        # DOWNLOAD HD REAL
        ydl_opts = {'format': 'bestvideo+bestaudio/best', 'outtmpl': f'{UPLOAD_FOLDER}/video_bruto.%(ext)s', 'overwrites': True, 'username': 'oauth2', 'password': ''}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_input = ydl.prepare_filename(info)

        lista_cortes = analisar_video_para_virais(video_input, densidade)
        resultados = []

        for i, tempo in enumerate(lista_cortes):
            nome = f"viral_{i}_{int(time.time())}.mp4"
            processar_legendas_finais(video_input, os.path.join(OUTPUT_FOLDER, nome), tempo, estilo)
            resultados.append({"titulo": f"Corte {i+1}", "arquivo": nome, "score": tempo['score'], "justificativa": tempo['justificativa']})

        return jsonify({"status": "sucesso", "cortes": resultados})
    except Exception as e: return jsonify({"status": "erro", "mensagem": str(e)})

@app.route('/download/<filename>')
def download(filename): return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == '__main__': app.run(debug=True, port=8000)