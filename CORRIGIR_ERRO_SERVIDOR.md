# CORRIGIR ERRO DO SERVIDOR - GUIA RAPIDO

## PROBLEMA PRINCIPAL: FALTA A CHAVE DA API DO GEMINI

O servidor precisa da chave da API do Google Gemini para funcionar.

---

## SOLUCAO EM 3 PASSOS:

### PASSO 1: Obter sua chave da API

1. Acesse: https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key" ou copie uma chave existente

### PASSO 2: Configurar o arquivo .env

1. Abra o arquivo `.env` que foi criado na pasta ViralCut_Pro
2. Substitua `COLOQUE_SUA_CHAVE_AQUI` pela chave que você copiou
3. Salve o arquivo

**Exemplo:**
```
GEMINI_API_KEY=AIzaSyDexemploKH9xJ2L3m4n5o6p7q8r9s0t1u2v3w
```

### PASSO 3: Iniciar o servidor

Execute um destes comandos:

```bash
# Opcao 1: Streamlit (recomendado para interface web)
streamlit run app_web.py

# Opcao 2: Flask
python servidor_flask.py

# Opcao 3: FastAPI
uvicorn api:app --reload --host 0.0.0.0 --port 5000

# Opcao 4: Usar o arquivo BAT
INICIAR_APP.bat
```

---

## AVISOS IMPORTANTES:

### 1. Biblioteca google-generativeai DEPRECIADA

Você está usando `google-generativeai` que foi descontinuada.
A Google recomenda migrar para `google-genai`.

**Para atualizar (opcional, mas recomendado):**
```bash
pip uninstall google-generativeai
pip install google-genai
```

Depois será necessário atualizar o código em `automacao_gemini.py`.

### 2. Se ainda der erro:

Verifique se você está usando o ambiente virtual correto:
```bash
# Ativar ambiente virtual (se usar)
.venv\Scripts\activate

# Verificar pacotes instalados
pip list
```

---

## TESTE RAPIDO:

Para testar se tudo está funcionando:

1. Certifique-se que o `.env` está configurado
2. Execute: `python servidor_flask.py`
3. Abra o navegador em: http://localhost:5000
4. Se a página carregar, o servidor está funcionando!

---

## PRECISA DE AJUDA?

Se o erro persistir, me envie:
1. A mensagem de erro COMPLETA que aparece no console
2. Qual comando você usou para iniciar o servidor
3. Print ou cópia do seu arquivo `.env` (SEM mostrar a chave completa)
