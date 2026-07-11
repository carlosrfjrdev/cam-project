---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-015 — Research Lane isolada com schema `research_*` próprio (Lead-Lag)

> **Data:** 2026-06-03
> **Status:** Aceita — aprovada pelo Founder
> **Lead:** Oscar · **Cross-cutting:** Kevin (SEC-GOV), Ada (dados)
> **Aprovador final:** Carlos Rodrigues Ferreira Junior (Founder)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-015-research-lane-isolada.md`

---

## 1. Contexto

A `SPEC-v0.5-LEADLAG-RESEARCH.md` materializa a fatia R0 + 1ª análise de lead-lag do
Cubo (research-only). Ela força três decisões arquiteturais que precisam ser registradas
antes do CODE:

1. **Onde mora o dado de research?** A tese (`CaM-RESEARCH-CUBO-LEADLAG`) assumia
   "Parquet/DuckDB importando de terceiros". O estado real é melhor: o **MT5 via bridge**
   (`GET_CANDLES`) já entrega OHLCV, e o TimescaleDB já tem `cam_market_ticks` e os
   continuous aggregates `cam_candles_*`. A tentação é reusar `cam_candles_*` como fonte
   da análise.
2. **A análise de research pode tocar tabelas do live?** O parecer consolidado das personas
   (`THESIS-ANALYSIS-01`, exigências de Kevin e Ada) é que o isolamento research↔live precisa
   ser **barreira técnica**, não texto.
3. **Como o slice de research se encaixa no Vertical Slice + Shared Kernel (ADR-013)?**

O Modo Dev Fase 0 (`DECISAO-FOUNDER-FASE0-DEV-MODE.md`) suspendeu a *cerimônia*
constitucional, mas manteve explicitamente o "sem execução real" e o isolamento — então
estas decisões valem mesmo no Modo Dev.

## 2. Decisão

**A Research Lane é um plano arquitetural próprio, com persistência em schema/namespace
`research_*` separado das tabelas operacionais (live), alimentado pelo MT5 (bridge
existente) e isolado do live por barreira técnica verificável.**

1. **Schema `research_*` próprio — NÃO reusar `cam_candles_*` como canônico.**
   A análise não lê os continuous aggregates do live como fonte de verdade. Tabelas novas:
   `research_bars` (canônico de barras, `timeframe` como coluna/partição), `research_data_sources`,
   `research_dataset_snapshots`, `research_runs`, `research_run_results`,
   `research_data_quality_checks`.
   **Razão:** `cam_candles_*` não têm provenance, calendário versionado, snapshot nem hash;
   são derivados de tick do live e mutáveis por política de retenção. Ancorar research neles
   (a) fere a reprodutibilidade (run imutável + hash composto — Ada) e (b) acopla research ao
   ciclo de vida do live (fere o isolamento — Kevin).

2. **MT5 é a fonte de research (via bridge read-only).** A ingestão usa o `GET_CANDLES`
   existente. A barra canônica é **M1** (`m1_is_primary`, Cenário B); M5…H1 são **derivadas
   determinísticas** de M1 (função pura, reprodutível byte a byte). H1 é computado **uma vez**
   (fronteira intraday↔swing). O caminho de dado é **read-only** sobre o MT5 (herda ADR-014).

3. **Isolamento research↔live como barreira de código (não comentário):**
   - O slice de research **não importa** Order Gateway, bridge de execução, `send_order`,
     `OrderSend` nem serviços operacionais — verificável por **import-linter** (contrato de
     independência/forbidden) + check de CI.
   - O serviço de research **não escreve** em `cam_orders`, `cam_positions`,
     `cam_journal_entries` nem equivalentes. Escrita restrita a `research_*` (idealmente
     role/usuário de banco de research sem grant nas tabelas live).
   - Namespace REST `/api/v1/research/*`. `DELETE` = cancel/archive/soft-delete (evidência
     nunca é apagada).
   - Nenhuma rota de research emite ordem, sinal operacional, direção ou sizing (Arts. 34º–36º).

4. **Encaixe no ADR-013:** a Research Lane é um (ou mais) **vertical slice** em
   `cam/features/research/...`. Reusa o Shared Kernel (`_shared/`) e segue a regra "features
   não se importam". O acoplamento com `mt5_integration` (fonte) é feito **na borda** (a rota
   de ingestão chama o bridge, ou um adaptador), nunca por import cruzado de domínio —
   coerente com ADR-013. Funções de cálculo (correlação defasada) são **puras** e podem
   reusar/estender `features/research/cross_asset_correlation.py` (Pearson já implementado).

## 3. Alternativas consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Reusar `cam_candles_*` (live) como fonte da análise | Sem provenance/calendário/snapshot/hash → quebra reprodutibilidade (run imutável). Acopla research ao ciclo do live (retenção/compressão) → fere isolamento. |
| 2 | Parquet + DuckDB como store de research (tese original) | DuckDB está na stack como motor analítico auxiliar, mas o **dado primário já chega via MT5→Postgres**. Introduzir um store de arquivos agora adiciona superfície (provenance em arquivo, sync, backup) sem ganho na fatia v0.5. Fica **LATER** se o volume de M1 multi-ano justificar (Parquet particionado `symbol/timeframe/session_date`). |
| 3 | Isolamento só por convenção (comentário/nomenclatura) | Parecer Kevin: convenção não é barreira. Um import acidental de execução ou um INSERT em tabela live passaria. Tem de ser import-linter + permissão. |
| 4 | Research dentro do mesmo slice do `mt5_integration` | Mistura fonte de dado de mercado (live, read-only do broker) com lógica de descoberta estatística. Slices distintos: `mt5_integration` provê candles; `research` consome e analisa. |

## 4. Consequências

### Positivas
- Reprodutibilidade real: snapshot + hash composto → rerun byte-idêntico (gate R0 automatizável).
- Isolamento auditável: import-linter + permissão de banco transformam "research não toca live"
  em fato verificável, não promessa.
- Aproveita o que já roda (bridge MT5, TimescaleDB, Pearson puro) — fatia honesta e barata.
- Não compromete o futuro: OFI/tick, DSR pleno, swing, Parquet/DuckDB entram como extensão.

### Negativas
- Duplicação aparente: `research_bars` re-armazena candles que "já existem" em `cam_candles_*`.
  É **intencional** — o preço da reprodutibilidade e do isolamento (igual à duplicação
  consciente que o ADR-013 já aceita).
- Mais um schema para migrar e versionar.

### Neutras
- DuckDB/Parquet permanecem na stack como opção analítica futura (não removidos).
- A barra canônica M1 e a derivação determinística viram contrato que SPECs futuras herdam.

### Controles SEC-GOV (Kevin) — condição de aceite
1. Contrato import-linter: `cam.features.research.*` **proibido** importar Order Gateway,
   `mt5_integration` de execução, `send_order`/`OrderSend`.
2. Escrita de research restrita a `research_*` (sem grant em tabelas live; ou assert no
   repository + check de CI).
3. Secrets de broker nunca em metadata de run, logs, payloads ou commit.

## 5. Custo de reversão

**Baixo–médio.** O schema `research_*` é aditivo e isolado; remover/trocar o store (ex.: migrar
para Parquet/DuckDB no futuro) afeta só o slice de research e sua migração — o contrato REST
`/api/v1/research/*` e as funções puras de cálculo permanecem estáveis. Não é decisão de fundação
do cockpit.

## 6. Referências

- SPEC: [`../specs/SPEC-v0.5-LEADLAG-RESEARCH.md`](../specs/SPEC-v0.5-LEADLAG-RESEARCH.md)
- SCOPE: [`../scopes/SCOPE-v0.5-LEADLAG-RESEARCH.md`](../scopes/SCOPE-v0.5-LEADLAG-RESEARCH.md)
- Teses: `../research/leadlag/` (CaM-RESEARCH-CUBO-LEADLAG, THESIS-ANALYSIS-01, THESIS-LEADLAG-PROPOSAL)
- DAS: [`../DAS.md`](../DAS.md) — §2 (camada de research) e §6 (modelo de dados) atualizados por esta ADR
- ADRs relacionadas: ADR-013 (vertical slice — research é slice), ADR-014 (MT5 read-only — fonte),
  ADR-005 (DuckDB analítico — store alternativo LATER), ADR-006 (IA sem autoridade)
- Código reaproveitável: `apps/cam-cockpit/backend/cam/features/research/cross_asset_correlation.py`
- Decisão Founder: `DECISAO-FOUNDER-FASE0-DEV-MODE.md` (isolamento permanece no Modo Dev)
