from moviepy import VideoFileClip, TextClip, CompositeVideoClip # Importação 2026
from moviepy.config import change_settings

# RESOLVE O ERRO [WinError 2]
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

def processar_legendas_finais(input_path, output_path, tempos, estilo):
    """
    Realiza o corte e aplica o design visual escolhido.
    """
    with VideoFileClip(input_path) as video:
        corte = video.subclip(tempos['start'], tempos['end'])
        
        # Estilo Hormozi Premium (Amarelo/Bold)
        if estilo == "Hormozi Premium":
            txt_clip = TextClip(
                text="OVERRIDE ACTIVE", 
                font_size=70, 
                color='yellow', 
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2,
                duration=corte.duration
            ).with_position(('center', 0.8), relative=True)
        else:
            txt_clip = TextClip(
                text="FOCUS MODE", 
                font_size=50, 
                color='white',
                bg_color='black',
                duration=corte.duration
            ).with_position('center')

        final_video = CompositeVideoClip([corte, txt_clip])
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")