# Guia de Testes - ViralCut Pro (SaaS Edition)

## Pré-requisitos
Certifique-se de que você tem o **Docker Desktop** instalado.
*Se não tiver Docker, você precisa instalar o Python e o Redis manualmente.*

## Opção 1: Rodando com Docker (Recomendado)
Essa é a opção mais fácil. O Docker sobe o Site, o Worker e o Redis tudo junto.

1. Abra o terminal na pasta do projeto.
2. Execute:
   ```powershell
   docker-compose up --build
   ```
3. Aguarde subir tudo.
4. Acesse: `http://localhost:5000`

## Opção 2: Rodando Manualmente (Sem Docker)
Você precisa de 3 terminais abertos.

**Terminal 1: Redis**
Garanta que o Redis está rodando na porta 6379.

**Terminal 2: O Site**
```powershell
# Ativar ambiente virtual (se tiver)
python run_production.py
```

**Terminal 3: O Worker**
```powershell
# Ativar ambiente virtual (se tiver)
# Precisa configurar a variável se não for localhost
python worker.py
```

---

## 🛑 Como Testar os Limites (Free vs Premium)

### Cenário 1: Usuário Free (Novo)
1. Acesse o site.
2. Coloque um e-mail novo (ex: `teste1@email.com`).
3. Envie um vídeo.
   - **Resultado Esperado:** O vídeo deve ser processado, mas virá em baixa qualidade (480p) e com a marca d'água "ViralCut Pro - Free".
4. Tente enviar um **segundo** vídeo com o **mesmo e-mail**.
   - **Resultado Esperado:** O site deve bloquear e mostrar o alerta: "LIMITE DIÁRIO ATINGIDO".

### Cenário 2: Usuário Premium
Como não tem compra real, vamos "fingir" que pagou editando o banco de dados.

1. Abra um terminal Python na pasta do projeto:
   ```powershell
   python
   ```
2. Execute os comandos para virar Premium:
   ```python
   import database
   database.add_user("seu@email.com", "approved")
   exit()
   ```
3. Agora volte no site e use o e-mail `seu@email.com`.
   - **Resultado Esperado:** Processamento ILIMITADO, Full HD (1080p) e SEM marca d'água.
