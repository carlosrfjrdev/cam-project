# Feature: ai_analyst

## Propósito

IA Auditora do CaM: analisa padrões de comportamento operacional do dia
de forma autonôma e pós-mercado. Opera exclusivamente em modo read-only
sobre dados do journal e decisões do Risk Engine.

Entrega análise textual via Telegram (notifier) após verificação obrigatória
pelo ContentGuard. Qualquer análise com conteúdo proibido é descartada e logada.

## I/O

**Input (read-only):**
- Journal entries do dia: asset, direction, result_net, adherence
- Risk Engine decisions do dia: validator, reason, approved

**Output:**
- Análise textual aprovada pelo ContentGuard
- Entregue via notificador (Telegram)
- Persistida no banco (T-H06)

## Artigos Constitucionais

| Artigo | Vinculação |
|--------|------------|
| **Art. 34º** | IA opera em modo auditoria — nunca executa ordens |
| **Art. 35º** | IA NÃO PODE: enviar ordem, desabilitar Risk Engine, justificar exceção |
| **Art. 36º** | Hierarquia constitucional inviolável |
| **Art. 31º** | Journal read-only — IA apenas lê, nunca escreve |

## Estrutura de módulos

```
ai_analyst/
├── README.md           ← este arquivo (contrato da feature)
├── content_guard.py    ← ContentGuard: verifica conteúdo proibido antes de entrega
├── data_collector.py   ← AnalystDataCollector: coleta read-only de journal + risk decisions
├── domain.py           ← entidades (stub Fase 0)
├── events.py           ← eventos publicados/consumidos (stub Fase 0)
├── prompts.py          ← build_analysis_prompt com restrições constitucionais embutidas
├── providers.py        ← OllamaProvider, AnthropicProvider, ProviderWithFallback
├── repository.py       ← persistência de análises (stub Fase 0, T-H06)
├── routes.py           ← GET /api/v1/ai-analyst/analyses (read-only)
├── scheduler.py        ← build_scheduler: cron 21:30 UTC (18:30 BRT pós-B3)
├── schemas.py          ← Pydantic schemas (stub Fase 0)
├── service.py          ← AIAnalystService: orquestra fluxo completo
└── tests/
    ├── test_ai_analyst_domain.py   ← T-G01: read-only, ContentGuard
    ├── test_providers.py           ← T-G02: Ollama, Anthropic, fallback
    └── test_analyst_service.py     ← T-G03: service completo, scheduler
```

## Anti-padrões

- **NUNCA** importar journal.service, kill_switch.service, fiscal.service ou harvest.service
- **NUNCA** adicionar métodos de escrita ao AnalystDataCollector
- **NUNCA** contornar ou desabilitar o ContentGuard
- **NUNCA** fazer o prompt sugerir ações de mercado ou ordens
- **NUNCA** entregar análise sem passar pelo ContentGuard primeiro
- **NUNCA** iniciar o scheduler sem aprovação do Founder

## Tech Debt

- `data_collector.py`: stubs sem banco — implementar com SQLAlchemy em T-H06
- `repository.py`: persistência de análises — implementar em T-H06
- `schemas.py`: Pydantic schemas para endpoints — implementar em T-H06
- `routes.py`: endpoints retornam stubs — implementar em T-H06
- `AnthropicProvider`: modelo hardcoded — carregar de config em T-H06
- Scheduler não ativado no lifespan do app — gate Founder antes de ativar
