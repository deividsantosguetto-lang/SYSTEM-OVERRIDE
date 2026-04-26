# 🚀 COMO USAR O OVERRIDE.AI

## ✅ Servidor Flask Está Rodando!

O servidor está ativo e pronto para processar seus vídeos.

## 🌐 Acessar o Site

### No seu computador:
**Abra o navegador e acesse:** http://localhost:5000

### Em outros dispositivos na mesma rede WiFi:
**Acesse:** http://192.168.0.12:5000

## 📝 Como Processar Vídeos

### Método 1: Link do YouTube

1. Acesse http://localhost:5000
2. Na aba **"Link (Stream)"**, cole o link do vídeo do YouTube
3. Escolha as configurações:
   - **Protocolo de Edição:** Hormozi / Caixa Focus / Raw Cut
   - **Densidade de Ataque:** Quantos cortes gerar (1-10)
   - **Janela de Retenção:** Auto / Curtos / TikTok / Longos
4. Clique em **"INICIAR OVERRIDE"**
5. Aguarde o processamento (pode demorar alguns minutos)
6. Os vídeos processados aparecerão automaticamente
7. Clique em **"BAIXAR ARQUIVO"** para fazer download

### Método 2: Upload de Arquivo

1. Acesse http://localhost:5000
2. Clique na aba **"Arquivo Local"**
3. Arraste ou clique para selecionar um vídeo MP4/MOV
4. Escolha as configurações (igual ao método 1)
5. Clique em **"INICIAR OVERRIDE"**
6. Aguarde o processamento
7. Baixe os cortes gerados

## ⚙️ O Que Acontece Durante o Processamento

1. **Download/Upload:** O vídeo é baixado ou recebido
2. **Análise IA:** O Gemini AI analisa o vídeo inteiro
3. **Identificação:** Detecta os momentos mais virais
4. **Geração:** Cria cortes de 30-60 segundos
5. **Legendas:** Adiciona legendas dinâmicas automáticas
6. **Resultado:** Vídeos prontos para postar no TikTok/Reels

## 📊 Informações dos Cortes

Cada corte mostra:
- **Título:** Nome do corte gerado pela IA
- **Score Viral:** Probabilidade de viralizar (0-100%)
- **Justificativa:** Por que esse momento é viral
- **Vídeo Preview:** Visualização direta
- **Botão Download:** Para baixar o arquivo

## 📁 Onde Ficam os Vídeos Processados

Os vídeos gerados são salvos em:
```
C:\Users\PC\Desktop\ViralCut_Pro\cortes\
```

## 🛑 Como Parar o Servidor

1. Vá no terminal onde o servidor está rodando
2. Pressione **Ctrl + C**

## 🔄 Como Reiniciar o Servidor

Se o servidor parar ou der erro:

```bash
cd C:\Users\PC\Desktop\ViralCut_Pro
python servidor_flask.py
```

## ⚠️ Resolução de Problemas

### O site não abre
- Verifique se o servidor está rodando (deve aparecer "Running on http://127.0.0.1:5000")
- Tente acessar http://127.0.0.1:5000 ao invés de localhost

### Erro no download do YouTube
- O YouTube pode bloquear alguns vídeos
- Tente com outro vídeo
- Use o método de Upload de Arquivo ao invés

### Processamento muito lento
- É normal! A IA precisa:
  - Analisar todo o vídeo
  - Transcrever o áudio
  - Identificar momentos virais
  - Gerar legendas
  - Renderizar cada corte
- **Vídeos de 10-20 minutos podem levar 5-10 minutos para processar**

### Erro de memória
- Feche outros programas
- Processe vídeos menores (máximo 30 minutos)
- Reduza a quantidade de cortes (use 1-3 ao invés de 10)

## 💡 Dicas de Uso

1. **Vídeos ideais:** 5-30 minutos de duração
2. **Melhor estilo:** Hormozi para vendas, Caixa Focus para retenção
3. **Quantidade:** Comece com 5 cortes, depois ajuste
4. **Duração:** Use "Auto" - a IA decide o melhor
5. **Teste:** Processe um vídeo pequeno primeiro para testar

## 🎯 Resultados Esperados

- **Entrada:** Vídeo de 20 minutos
- **Saída:** 5 cortes de 30-60 segundos cada
- **Cada corte tem:**
  - Legenda dinâmica sincronizada
  - Momentos de alta retenção
  - Pronto para postar sem edição

## 📞 Status Atual

✅ Servidor Flask: RODANDO
✅ yt-dlp: Atualizado (v2026.1.31)
✅ Interface: Funcionando
✅ Rotas: Todas implementadas
✅ Processamento: Operacional

---

**TUDO PRONTO PARA USAR!** 🎉

Acesse agora: http://localhost:5000
