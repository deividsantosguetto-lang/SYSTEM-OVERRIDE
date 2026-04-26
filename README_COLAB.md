# Override.AI — ViralCut Pro no Google Colab

Guia completo para rodar o servidor no Colab com GPU gratuita e URL pública via ngrok.

---

## Pré-requisitos

| Item | Onde obter |
|------|-----------|
| Conta Google | google.com |
| Chave Gemini | [aistudio.google.com](https://aistudio.google.com) → Get API Key |
| Token ngrok | [ngrok.com/dashboard](https://dashboard.ngrok.com) → Your Authtoken |
| Token do bot Telegram | [@BotFather](https://t.me/BotFather) → /newbot (opcional) |

---

## Passo a passo

### 1. Prepare os arquivos no Google Drive

1. Abra o Google Drive
2. Crie uma pasta chamada **`ViralCut_Pro`** (ou o nome que preferir)
3. Faça upload dos seguintes arquivos para essa pasta:
   ```
   api.py
   motor_novo.py
   automacao_gemini.py
   jarves.py
   tasks.py
   arialbd.ttf          ← fonte das legendas (inclua se tiver)
   templates/
   ├── index.html
   └── galeria.html
   ```

> Se o nome da pasta for diferente, ajuste `DRIVE_PATH` na Célula 2.

---

### 2. Abra o notebook no Colab

1. Acesse [colab.research.google.com](https://colab.research.google.com)
2. Menu `Arquivo → Fazer upload do notebook`
3. Selecione o arquivo `colab_override.ipynb`

**Recomendado: ative a GPU antes de começar**
> `Runtime → Change runtime type → Hardware accelerator → T4 GPU`

---

### 3. Execute as células em ordem

#### Célula 1 — Instala dependências
Instala todos os pacotes Python necessários e o `ffmpeg` via apt.
Tempo: ~2 min (primeira vez).

#### Célula 2 — Copia arquivos do projeto
Monta o Google Drive e copia os arquivos para `/content/viralcut/`.

- Se aparecer ❌ para algum arquivo: verifique o `DRIVE_PATH` e se o arquivo está no Drive.
- A fonte `arialbd.ttf` é opcional — se não estiver disponível, uma fonte Linux é usada como fallback.

#### Célula 3 — Configura chaves de API
Vai pedir cada chave separadamente (campos mascarados):

| Campo | Obrigatório? |
|-------|-------------|
| GEMINI_API_KEY | ✅ Sim |
| TELEGRAM_BOT_TOKEN | Não (Jarves desativado sem ele) |
| NGROK_AUTHTOKEN | ✅ Sim |
| API_TOKEN | ✅ Sim (crie qualquer senha) |

As chaves são salvas em `.env` dentro do Colab — **não ficam visíveis no notebook**.

#### Célula 4 — Inicia ngrok + servidor
1. Conecta ao ngrok e exibe a **URL pública**
2. Atualiza o `jarves.py` para apontar para essa URL
3. Sobe o servidor FastAPI em background

```
══════════════════════════════════════════════════════
  🌐 URL PÚBLICA : https://abc123.ngrok-free.app
  🎬 Painel      : https://abc123.ngrok-free.app/
  📡 API docs    : https://abc123.ngrok-free.app/docs
══════════════════════════════════════════════════════
```

Acesse a URL pública pelo celular ou computador — o painel está no ar.

---

## Usar múltiplas chaves Gemini (evita rate limit)

Adicione mais chaves ao `.env` antes de iniciar o servidor. Na Célula 3, ao criar o arquivo, inclua linhas extras. Ou edite o arquivo manualmente após a criação:

```python
# Rode numa célula nova após a Célula 3:
with open('/content/viralcut/.env', 'a') as f:
    f.write('GEMINI_API_KEY_2=sua_segunda_chave\n')
    f.write('GEMINI_API_KEY_3=sua_terceira_chave\n')
```

---

## Reabrir uma sessão existente

Ao reabrir o Colab, a sessão é **zerada** (RAM limpa). Para reativar:

1. Execute a **Célula 1** novamente (dependências precisam ser reinstaladas)
2. Execute a **Célula 2** para recopiar os arquivos
3. Execute a **Célula 3** para recriar o `.env`
4. Execute a **Célula 4** — nova URL ngrok será gerada

> Dica: salve as chaves num lugar seguro para colar rapidamente na Célula 3.

---

## Atualizar os arquivos do projeto

Se você modificou `api.py`, `motor_novo.py` ou outro arquivo localmente:

1. Faça upload da versão nova para a mesma pasta no Drive
2. Execute a Célula 2 novamente (sobrescreve os arquivos)
3. Execute a Célula 4 novamente (reinicia o servidor)

---

## Solução de problemas

| Erro | Causa | Solução |
|------|-------|---------|
| `❌ api.py não encontrado` | `DRIVE_PATH` errado | Ajuste o caminho na Célula 2 |
| `ngrok.connect() failed` | Token ngrok inválido | Verifique em ngrok.com/dashboard |
| `ModuleNotFoundError` | Célula 1 não foi executada | Execute a Célula 1 primeiro |
| `Port 8000 already in use` | Servidor rodando ainda | Execute `ngrok.kill()` e reexecute a Célula 4 |
| Vídeo não baixa | yt-dlp desatualizado | `!pip install -q -U yt-dlp` em nova célula |
| Legenda sem som | ffmpeg não instalado | Execute `!apt-get install -y ffmpeg` |

---

## Notas importantes

- **URL muda a cada sessão** — informe a nova URL para os usuários do painel sempre que reiniciar
- **Sessão dura ~12h** no Colab gratuito — após isso, precisa reexecutar tudo
- **GPU T4 acelera o Whisper** — ative em `Runtime → Change runtime type` antes da Célula 1
- Os cortes gerados ficam em `/content/viralcut/cortes/` e são deletados quando a sessão fecha — faça download ou mova para o Drive se precisar salvar
