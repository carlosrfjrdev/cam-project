# RUNBOOK — Obter as chaves de API de IA (Anthropic / OpenAI)

> **Objetivo:** obter e configurar as API keys que o **Trade Analyzer** do CAM usa
> para enviar as operações à IA. O provider é selecionável na tela — você pode
> configurar **uma** (Claude **ou** OpenAI) ou as duas.
>
> **Onde as chaves vivem:** `apps/cam-cockpit/backend/.env`
> (variáveis `ANTHROPIC_API_KEY` e `OPENAI_API_KEY`).
> ⚠️ O `.env` **nunca** é commitado (bloqueado por `.gitignore` + pré-commit hook).
> Trate a chave como senha: não cole em chat, issue, screenshot ou commit.

---

## Parte A — Chave da Anthropic (Claude)

1. Acesse **https://console.anthropic.com** e crie a conta / faça login.
2. **Adicione crédito** (a API é paga e separada da assinatura do Claude.ai):
   - Menu **Billing** → **Add credits** (ou **Set up payment**). Comece com um valor
     pequeno (ex.: US$ 5). A API funciona em pré-pago/crédito.
3. **Gere a chave:**
   - Menu **API Keys** (ou **Settings → API Keys**) → **Create Key**.
   - Dê um nome (ex.: `cam-trade-analyzer`) e clique em criar.
   - **Copie a chave AGORA** — ela começa com `sk-ant-...` e **só é exibida uma vez**.
     Se perder, revogue e gere outra.
4. (Opcional) Em **Limits**, defina um **spend limit** mensal para não estourar custo.

**Modelo usado pelo CAM:** definido em `anthropic_model` (default
`claude-haiku-4-5-20251001` — barato e rápido). Para análises mais profundas, troque
no `.env` para um modelo Sonnet/Opus (ver `claude-api` / docs Anthropic para os IDs).

---

## Parte B — Chave da OpenAI (GPT)

1. Acesse **https://platform.openai.com** e crie a conta / faça login.
   - ⚠️ É a **plataforma de API** (`platform.openai.com`), diferente do ChatGPT.
2. **Adicione crédito / método de pagamento:**
   - **Settings → Billing** → adicionar cartão e crédito (ex.: US$ 5).
   - Sem crédito a API retorna erro `insufficient_quota`.
3. **Gere a chave:**
   - Menu **API keys** (**https://platform.openai.com/api-keys**) → **Create new secret key**.
   - Nome (ex.: `cam-trade-analyzer`) → criar.
   - **Copie AGORA** — começa com `sk-...` e **só aparece uma vez**.
4. (Opcional) **Settings → Limits** → defina um **usage limit** mensal.

**Modelo usado pelo CAM:** `openai_model` (default `gpt-4o-mini` — barato). Trocável no `.env`.

---

## Parte C — Configurar no CAM

1. Abra `apps/cam-cockpit/backend/.env`.
2. Preencha a(s) chave(s) — basta a do provider que você vai usar:

   ```dotenv
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
   ```

   (Opcional — trocar de modelo:)
   ```dotenv
   ANTHROPIC_MODEL=claude-haiku-4-5-20251001
   OPENAI_MODEL=gpt-4o-mini
   ```

3. **Reinicie o backend** (ele lê o `.env` no startup):
   ```
   cd apps/cam-cockpit/backend
   uv run uvicorn cam.api.main:app --host 127.0.0.1 --port 8000
   ```

---

## Parte D — Verificar

Cheque qual provider o CAM reconhece como configurado:

```
curl -s http://127.0.0.1:8000/api/v1/trade-analyzer/providers
```

- `"configured": true` → chave carregada, provider pronto.
- `"configured": false` → chave vazia/errada (revise o `.env` e reinicie).

Na UI (`/trade-analyzer`), o chip ao lado do seletor mostra **verde "modelo pronto"**
ou **amarelo "sem API key"**. Com a chave OK, suba um report e clique **Analisar**.

---

## Notas de custo e segurança

- **Custo:** o analyzer manda só um **resumo de métricas** (JSON pequeno) + a narrativa
  volta em texto — gasto por análise é baixo nos modelos `haiku`/`gpt-4o-mini`.
  Ainda assim, configure **spend limits** nos dois consoles.
- **Privacidade:** os números das suas operações saem do ambiente local para o provider
  escolhido. Se isso for sensível, prefira **Ollama local** (já suportado pela infra de
  IA do CAM) — fora do escopo deste runbook.
- **Rotação:** se uma chave vazar, **revogue no console** e gere outra; atualize o `.env`.
- **Nunca** commite o `.env`. Se commitar por acidente, revogue a chave imediatamente.
