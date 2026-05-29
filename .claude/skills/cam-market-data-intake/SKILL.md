---
name: cam-market-data-intake
description: "CaM Market Data Intake (DRAFT). Acionar para ingerir tick/candle/book de qualquer fonte com provenance completa, dedupe e checagem de qualidade. Lead Ada (+Wyck). Dado sem provenance não entra. Ancoragem Pilar 4 + gate de dados. CaM-only / Stage 0."
phase: cam-financeiro
lead_persona: Ada
co_lead_persona: Wyck (leitura de fluxo/microestrutura)
status: draft (esqueleto — Stage 0 / execução manual via Founder)
---

# Skill — cam-market-data-intake (DRAFT)

> Skill do **mundo financeiro do CaM** (CaM-only). Lead: **Ada**. Esqueleto / Stage 0.

## 1. Propósito

Ingerir dados de mercado (tick/candle/book) de qualquer fonte com **provenance completa**, dedupe e checagem de qualidade. Dado sem proveniência não entra no CaM.

## 2. Quando acionar

- Ingestão de tick/candle/book de fonte nova ou recorrente.
- Importação de histórico (CSV/Parquet) ou stream (MT5/bridge).

## 3. Lead + co-personas

- **Lead:** Ada (dados / banco / provenance).
- **Co:** Wyck (consome book/fluxo para microestrutura).

## 4. Procedimento (rascunho)

1. **Receber** lote/stream (fonte, tipo, ativo).
2. **Provenance** — registrar fonte, tipo, ativo, ts origem/ingestão, hash, qualidade, gaps, custo, uso permitido (ToS).
3. **Dedupe** por hash determinístico.
4. **Quality flags** — has_gaps, has_zero_volume, out_of_hours.
5. **Persistir** com proveniência atrelada.

## 5. Artefatos in/out

- **In:** lote/stream de mercado + metadados de fonte.
- **Out:** dado normalizado + registro de provenance + quality flags.

## 6. Gates

- **Dado sem provenance não entra** — gate de dados.
- ToS não aceito → ingestão bloqueada.
- Stage 0: ingestão manual/governada; sem automação de operação.

## 7. Ancoragem constitucional

- **Pilar 4** (book L2 / dados de mercado), gate de dados da Vision, provenance obrigatório.

> Procedimento detalhado = demanda futura. DRAFT / Stage 0. (Backend de provenance já existe em `cam_market_data_provenance` — BL-B.)
