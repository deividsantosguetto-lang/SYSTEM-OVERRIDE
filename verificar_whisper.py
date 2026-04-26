import whisper
import os
import sys

def teste_rapido():
    print("Iniciando teste do Whisper...")
    try:
        # Tenta carregar o modelo 'tiny' que é o mais leve para teste rápido
        print("Carregando modelo 'tiny'...")
        model = whisper.load_model("tiny")
        print("Modelo carregado com sucesso!")
        
        # Teste com um arquivo de áudio dummy se necessário, mas primeiro só o load já valida a biblioteca
        # Para testar transcrição, precisaria de um audio. 
        # Vou tentar extrair 2 segundos do teste.mp4 para testar transcrição real.
        
        import subprocess
        
        video_path = os.path.abspath("estoque/teste.mp4")
        audio_path = os.path.abspath("teste_audio_whisper.wav")
        ffmpeg_path = os.path.abspath("ffmpeg.exe")
        
        print(f"Extraindo áudio de {video_path}...")
        
        # Extrai 2 segundos
        cmd = [
            ffmpeg_path, "-y",
            "-i", video_path,
            "-ss", "0",
            "-t", "5",
            "-vn",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            audio_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        if os.path.exists(audio_path):
            print("Áudio extraído. Transcrevendo...")
            result = model.transcribe(audio_path, fp16=False) # fp16=False para compatibilidade CPU
            print("Transcrição resultante:")
            print(result["text"])
            
            # Limpeza
            try:
                os.remove(audio_path)
            except:
                pass
            print("\nTESTE WHISPER: SUCESSO! ✅")
        else:
            print("Falha ao extrair áudio.")
            
    except Exception as e:
        print(f"\nERRO NO TESTE WHISPER: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_rapido()
