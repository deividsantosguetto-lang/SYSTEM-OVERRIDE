from google import genai

import os

# Pega a chave do ambiente (Seguro)
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

CHAVE_API = os.environ.get("GEMINI_API_KEY")

if not CHAVE_API:
    print("ERRO: A variavel GEMINI_API_KEY nao foi definida!")
    exit(1)

client = genai.Client(api_key=CHAVE_API)

print("--- REQUISITANDO MODELOS DISPONÍVEIS ---")
try:
    # Lista apenas os nomes para não ter erro de atributo
    for model in client.models.list():
        print(f"-> {model.name}")
except Exception as e:
    print(f"Erro ao acessar a API: {e}")