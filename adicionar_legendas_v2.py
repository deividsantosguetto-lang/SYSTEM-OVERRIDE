import os
# Configuração do ImageMagick
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

# IMPORTAÇÕES DIRETAS (A prova de falhas para 2026)
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from automacao_gemini import transcrever_audio_real

def processar_legendas_finais(input_path, output_path, tempos, estilo):
    font_path = r"C:\Windows\Fonts\arialbd.ttf" # Fonte Negrito Real

    try:
        with VideoFileClip(input_path) as video:
            # 1. CORTE E ENQUADRAMENTO TIKTOK (Foco no Rosto/Topo)
            corte = video.subclipped(tempos['start'], tempos['end']) # Versão 2.0 usa subclipped
            w, h = corte.size
            target_w = h * (9/16)
            
            # Centraliza no rosto (mantém o topo y1=0)
            video_vertical = corte.cropped(x1=(w-target_w)/2, y1=0, x2=(w+target_w)/2, y2=h)
            video_final = video_vertical.resized(height=1080)

            # 2. TRANSCRIÇÃO REAL
            falas = transcrever_audio_real(input_path)
            labels = []
            
            for f in falas:
                if f['start'] >= tempos['start'] and f['end'] <= tempos['end']:
                    t_start = f['start'] - tempos['start']
                    t_end = f['end'] - tempos['start']
                    
                    txt = TextClip(
                        text=f['text'].upper(), font_size=80, color='yellow' if estilo == "Hormozi Premium" else 'white',
                        font=font_path, stroke_color='black', stroke_width=3, method='label'
                    ).with_start(t_start).with_end(t_end).with_position(('center', 0.8), relative=True)
                    labels.append(txt)

            # 3. RENDERIZAÇÃO EM ALTÍSSIMA QUALIDADE
            final = CompositeVideoClip([video_final] + labels)
            final.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac", 
                fps=30, 
                bitrate="8000k", # Qualidade cristalina
                logger='bar'     # Mostra a barra de progresso no terminal
            )
            
            final.close(); video_final.close()

    except Exception as e:
        print(f"Erro no processamento: {e}")