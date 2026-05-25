---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-002 — Python 3.12 + FastAPI como Backend do Cockpit

> **Data:** 2026-05-24
> **Status:** Aceita
> **Lead:** Oscar
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-002-python-fastapi-backend.md`

---

## 1. Contexto

O CaM precisa de um backend que:
- implemente o Risk Engine como módulo Pure Python (sem I/O) com 100% de cobertura de testes
- exponha APIs REST e WebSocket para o frontend local
- integre com PostgreSQL+TimescaleDB, Telegram, Ollama e Anthropic
- rode tanto em Linux (desenvolvimento) quanto em Windows 11 (produção)
- permita desenvolvimento agêntico eficiente (context-first, legibilidade)

O domínio quant-finance é historicamente Python-first: scipy, numpy, pandas, hypothesis, vectorbt, DuckDB — todas as bibliotecas críticas para backtesting e análise de estratégia existem natively em Python.

A stack Teczilabs usa NestJS/Java para outros produtos. O CaM explicitamente **revoga** esses combos (ADR-000-override-stack) pois foram inferidos para produtos comerciais multi-usuário — não se aplicam a cockpit local mono-usuário com domínio quant.

---

## 2. Decisão

O backend do CaM Cockpit usa Python 3.12 + FastAPI como framework web/API. Stack completa:

| Componente | Tecnologia | Versão alvo |
|---|---|---|
| Linguagem | Python | 3.12.x |
| Framework web/API | FastAPI | 0.115+ |
| ASGI server | Uvicorn | 0.32+ |
| Validação de schema | Pydantic v2 | 2.x |
| ORM | SQLAlchemy 2.0 async | 2.0.x |
| Driver DB | psycopg[binary] | v3 |
| Migrations | Alembic | 1.13+ |
| Gerência de deps | uv | latest |
| Lint/format | ruff | latest |
| Type check | mypy ou pyright | latest |
| Testes | pytest + pytest-asyncio + hypothesis | latest |
| Logs estruturados | structlog | 24+ |
| Scheduler | APScheduler | latest |
| Arquitetura imports | import-linter | — |

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | NestJS (TypeScript) | Stack Teczilabs padrão, mas domínio quant é Python — sem equivalente às bibliotecas de análise financeira; desenvolvimento do Risk Engine em TS seria mais verboso e sem ecosystem quant |
| 2 | Django + DRF | ORM Django não é async-first; overhead de admin, ORM migrations e configuração para projeto mono-usuário; FastAPI + SQLAlchemy 2.0 é mais leve e async-nativo |
| 3 | Flask + Celery | Mais setup manual para async, WebSocket, validação de schema; FastAPI resolve tudo nativamente com menos código |
| 4 | Java / Spring Boot | Não há justificativa para JVM em projeto pessoal mono-usuário; tooling quant inexistente; overhead de build e configuração |

---

## 4. Consequências

### Positivas
- Python é a linguagem padrão de quant finance — numpy, pandas, scipy, vectorbt, hypothesis disponíveis sem adapter
- FastAPI é async-nativo — WebSocket e background jobs sem fricção
- Pydantic v2 torna contracts e validação de schema triviais
- SQLAlchemy 2.0 async + psycopg3 + Alembic é stack madura e bem documentada
- uv é significativamente mais rápido que pip/poetry para gerência de deps
- ruff combina lint + format em uma única ferramenta
- hypothesis é a biblioteca de property-based testing mais madura em Python — essencial para Risk Engine

### Negativas
- GIL do Python pode ser limitante para tick streaming de alta frequência (mitigado: 1 ativo, 50–100ms de tick, não é HFT)
- Async Python tem curvas de aprendizado para debugging de coroutines
- Deploy em Windows exige atenção a paths e encoding (mitigado por ADR-012 — pathlib, cross-platform)

### Neutras
- Hot path pode ser otimizado com Cython/Rust se profiling mostrar necessidade real (improvável em 1 ativo)
- Frontend gerado via OpenAPI → TypeScript client (TanStack Query) — contrato bem definido

---

## 5. Custo de Reversão

**Médio-Alto** — mudar de Python para outra linguagem exigiria reescrever o Risk Engine (módulo crítico constitucional), o backtest engine e todas as integrações. O custo é alto em termos de tempo, mas não há lock-in de fornecedor além do ecosystem quant Python.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §5, §6.2
- ADRs relacionadas: ADR-007 (Risk Engine Pure Python), ADR-013 (Vertical Slice)
