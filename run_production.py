from waitress import serve
from servidor_flask import app
import os

print("=================================================")
print("  VIRALCUT PRO - SERVIDOR DE PRODUÇÃO (ASYNC)   ")
print("=================================================")
print("  > Modo: Multi-Thread (Waitress)")
print("  > Porta: 5000")
print("  > ACESSE EM: http://localhost:5000")
print("=================================================")

# Configuração para produção
port = int(os.environ.get("PORT", 5000))
print(f"  > Detectado PORT env: {port}")

# threads=2 para economizar RAM no plano gratuito
serve(app, host='0.0.0.0', port=port, threads=2)
