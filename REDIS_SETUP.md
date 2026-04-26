# Configuração do Redis e Worker

Para usar o novo sistema de filas (que aguenta milhares de acessos), você precisa de duas coisas novas:

1.  Um servidor **Redis** rodando.
2.  Um processo **Worker** rodando (o "operário" que faz o trabalho pesado).

## 1. Instalar Redis (Windows)

Como você está no Windows e não está usando Docker Desktop no momento, a opção mais fácil é baixar a versão portada:

1.  Baixe o instalador mais recente aqui: [Redis-x64-3.0.504.msi](https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi) (Link oficial da Microsoft Archive) ou use o Memurai (compatível).
2.  Instale e deixe rodando (ele vira um Serviço do Windows).

*Opção Alternativa (Se tiver WSL2 ou Docker):*
`docker run -d -p 6379:6379 redis`

## 2. Como Rodar o Projeto Agora

Você vai precisar de **dois terminais** abertos ao mesmo tempo.

**Terminal 1 (O Site):**
```powershell
python run_production.py
```
*Isso sobe o site. Ele recebe o pedido e coloca na fila.*

**Terminal 2 (O Operário/Worker):**
```powershell
python worker.py
```
*Isso liga o processamento. Ele olha pra fila e processa os vídeos.*

---

## 3. Configuração no Koyeb (Nuvem)

Na nuvem é mais fácil, você não instala nada.

1.  Crie um Database/Redis no Koyeb (ou use o **Upstash Redis** que tem plano grátis).
2.  Pegue a URL de conexão (começa com `redis://...`).
3.  No seu serviço do ViralCut Pro no Koyeb, adicione a Variável de Ambiente:
    *   **Key:** `REDIS_URL`
    *   **Value:** `redis://default:senha@url-do-redis:6379`

Pronto! O código já está preparado para ler essa variável e se conectar.
