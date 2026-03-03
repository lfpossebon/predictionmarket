# HEARTBEAT.md

## 📱 **Canal de Comunicação**
- **OFICIAL:** Telegram — canal único e confiável

## Tarefas Periódicas



### Sync Supabase (sob demanda, NÃO periódico)
- NÃO rodar sync completo automaticamente (731 arquivos = 53min + custo OpenAI)
- Só sincronizar quando LFP pedir ou quando houver arquivo novo relevante
- Script: `scripts/rag-knowledge-sync.py` (precisa OPENAI_API_KEY e SSL_CERT_FILE)
- Base atual: ~52.766 chunks + 12 chunks dos concorrentes (subidos 2026-02-18)
- Alertas conhecidos: 34 docs sem fonte, 7 a classificar, 12 sem conteúdo

### Not Journal - Resumo Diário (PENDENTE)
- A definir melhor solução com LFP
- Site tem menos conteúdo que o canal do WhatsApp
- Explorar alternativas amanhã

### 🧠 Memória Diária (OBRIGATÓRIO - todo heartbeat após 22h)
1. Ler conversa do dia com LFP (histórico da sessão)
2. Atualizar `memory/YYYY-MM-DD.md` com tudo relevante
3. Atualizar `MEMORY.md` com decisões/aprendizados importantes
4. **NUNCA** começar o dia seguinte sem saber o que aconteceu no anterior
5. LFP exigiu isso explicitamente — é prioridade máxima

### 📦 GitHub Push Workspace (OBRIGATÓRIO - todo heartbeat após 22h)
1. `cd ~/clawd && git add . && git status`
2. Se houve mudanças relevantes: `git commit -m "🔮 Atualização workspace — YYYY-MM-DD"`
3. `git push` para manter sincronizado
4. Foco: arquivos de configuração, memória, docs importantes
