---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-004 — PostgreSQL 16 + TimescaleDB desde Fase 0 (revoga SQLite)

> **Data:** 2026-05-24
> **Status:** Aceita
> **Lead:** Oscar
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-004-postgresql-timescaledb.md`

---

## 1. Contexto

Uma proposta anterior sugeria SQLite como banco de dados do MVP para simplicidade de setup. Esta ADR revoga essa proposta.

O CaM precisa armazenar e analisar:
- **Tick data em volume massivo:** 1 ativo (WIN ou WDO) em horário de pregão (10h–18h) com tick a 50–100 ms gera 300k–600k ticks/dia. Dois ativos, dois anos de histórico para backtest sólido = 400M–800M registros.
- **Análise de padrões em estratégias:** window functions complexas, time-bucketing arbitrário (1s, 5s, 1m, 5m, 15m, 1h), gap-fill, agregações estatísticas (percentil, stddev móvel, ATR, ADX), correlações cross-ativo.
- **JOIN entre tick data e dados operacionais:** cruzar tick data com cam_trades, cam_risk_decisions é trivial em Postgres, inviável em SQLite + Python puro.
- **Auditoria fiscal e operacional por tempo indefinido** — tabelas de journal, risk_decisions e fiscal nunca podem ser dropadas.

Mudar de SQLite para Postgres no meio do projeto (quando o volume de tick tornar SQLite impossível) sai mais caro em tempo e risco do que configurar Docker Desktop + WSL2 uma vez desde o início.

---

## 2. Decisão

PostgreSQL 16 com extensão TimescaleDB é o banco transacional **e** de séries temporais do CaM **desde o primeiro commit**.

**Container:** `timescale/timescaledb:latest-pg16` via `docker-compose.yml` no repo do app.

**Hypertables (TimescaleDB):**
- `cam_market_ticks` — chunk 1 dia, compressão após 7 dias, reorder após 30 dias
- `cam_market_book_snapshots` — chunk 1 dia, compressão após 3 dias, drop após 90 dias

**Continuous aggregates (Timescale):**
- `cam_candles_1s`, `cam_candles_5s`, `cam_candles_1m`, `cam_candles_5m`, `cam_candles_15m`, `cam_candles_1h`, `cam_candles_1d`
- Criados via `CREATE MATERIALIZED VIEW ... WITH (timescaledb.continuous)`

**Retenção:**
- Tick data: indefinida + compressão
- Journal, risk_decisions, violations, fiscal: **infinita** (memória institucional)
- Backtest: configurável por run

**Backup:**
- `pg_dump` diário automatizado
- `rclone` para Google Drive sync noturno
- Journal duplo: Postgres + JSONL append-only em `~/.cam/journal/YYYY-MM-DD.jsonl` (fallback para falha catastrófica com posição aberta — Art. 19º)

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | SQLite (proposta anterior) | Não foi feito para 400M–800M registros de tick data; análise de padrões com window functions complexas é dolorosa; sem time-bucketing nativo; sem compressão automática; sem continuous aggregates |
| 2 | InfluxDB para time series + Postgres para operacional | Dois bancos = dois schemas, dois backups, dois deploys, dois clientes; JOIN cross-banco é impossível nativamente; TimescaleDB elimina a necessidade de InfluxDB ao oferecer time series nativa no Postgres |
| 3 | MongoDB para flexibilidade de schema | Sem JOIN eficiente; sem window functions; sem time-bucketing; domínio operacional do CaM é altamente relacional (audit trail, fiscal, reconciliação) |
| 4 | QuestDB | Excelente para time series mas sem ecosystem transacional maduro; sem suporte nativo a domínio operacional misto |

---

## 4. Consequências

### Positivas
- TimescaleDB é extensão do Postgres — mesmo SQL, mesmo driver (psycopg3), mesma migration tool (Alembic)
- Compressão Timescale: tick antigo comprime 10–95× — sem isso, 800M ticks = centenas de GB
- Continuous aggregates: candles em vários timeframes pré-agregados e atualizados em background — backtest e dashboard consultam pré-agregados em ms
- Hyperfunctions: `time_bucket`, `first/last`, `histogram`, `time_weight`, `interpolate`, `locf` — primitivas que substituem dezenas de linhas de Python
- Retenção diferenciada: tabelas operacionais ficam para sempre; tick bruto comprime progressivamente
- Journal duplo (Postgres + JSONL) garante registro mesmo em falha catastrófica de banco com posição aberta

### Negativas
- Requer Docker Desktop no Windows 11 (com WSL2) — overhead inicial de configuração
- Mais pesado que SQLite para desenvolvimento — mas Docker já é praticamente padrão
- TimescaleDB adiciona complexidade à migration inicial (CREATE EXTENSION, hypertables, continuous aggregates)

### Neutras
- Linux dev: Docker nativo (já instalado: Docker 29.1) — sem overhead
- Windows prod: Docker Desktop + WSL2 — instalação única, depois transparente

---

## 5. Custo de Reversão

**Alto** — mudar de Postgres+Timescale para outro banco após criar hypertables, continuous aggregates e começar a acumular tick data seria uma migração de dados complexa. Esta é uma decisão de fundação.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md) §5 e §8
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §6.4
- ADRs relacionadas: ADR-005 (DuckDB complementar), ADR-002 (SQLAlchemy 2.0 como ORM)
