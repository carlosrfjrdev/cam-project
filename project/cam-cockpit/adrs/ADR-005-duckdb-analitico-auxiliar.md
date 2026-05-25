---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-005 — DuckDB como Motor Analítico Auxiliar (Read-Only sobre Arquivos)

> **Data:** 2026-05-24
> **Status:** Aceita
> **Lead:** Oscar
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-005-duckdb-analitico-auxiliar.md`

---

## 1. Contexto

O CaM possui dois contextos analíticos distintos:

1. **Operacional/live:** dados transacionais e de série temporal do cockpit (Postgres+Timescale — ADR-004)
2. **Research exploratório:** análise ad-hoc em dados exportados do Profit (CSV/Parquet), notebooks Jupyter, experimentos de backtest isolados sem poluir o banco operacional

Para o contexto de research, Postgres é over-engineering: requer servidor rodando, conexão, schema definido. DuckDB é um motor SQL em processo (zero-config, zero-servidor) que lê diretamente CSV, Parquet, JSON — ideal para análise ad-hoc.

---

## 2. Decisão

DuckDB **complementa** Postgres+Timescale como motor analítico auxiliar para research exploratório. **Não substitui** o banco operacional.

**Casos de uso permitidos:**
- Research exploratório em CSV/Parquet exportados do Profit (importação inicial antes de virar hypertable Timescale)
- Notebooks Jupyter de pesquisa quant onde Carlos quer fazer query SQL em arquivo local sem subir nada
- Backtest em datasets isolados (um experimento específico) sem poluir o Postgres operacional
- Prototipagem de queries analíticas antes de migrar para Timescale

**Restrição inviolável:**
- DuckDB **nunca grava em tabela vista pelo cockpit live**
- DuckDB é **read-only sobre arquivos** no contexto do CaM
- Resultados de análise DuckDB não alimentam automaticamente o Risk Engine ou o Journal

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Pandas + Python puro para research | DuckDB é significativamente mais rápido que Pandas para queries analíticas em datasets grandes; SQL é mais expressivo para exploração ad-hoc |
| 2 | Usar apenas Postgres+Timescale | Overhead de servidor e schema para análise ad-hoc em arquivo local; Jupyter + Postgres require psycopg connection management; DuckDB `SELECT * FROM 'file.csv'` é zero-friction |
| 3 | Apache Spark | Absurdo de overhead para 1 operador analisando dados de 1–2 ativos |

---

## 4. Consequências

### Positivas
- Zero-config: `import duckdb; duckdb.query("SELECT * FROM 'data.csv'")` — sem servidor, sem schema
- Performance superior ao Pandas para aggregations analíticas em arquivos grandes
- Complementa Timescale sem substituí-lo — cada ferramenta no seu contexto
- Notebooks Jupyter com DuckDB são a ferramenta natural de research quant de Carlos

### Negativas
- Risco de confundir contextos: DuckDB para análise exploratória vs. Postgres para dados operacionais
- A separação precisa ser disciplinada — nenhum dado de DuckDB deve alimentar diretamente decisões do cockpit sem passar pela camada de serviço do backend

### Neutras
- DuckDB lê Parquet — formato de exportação ideal do Profit (se disponível) ou exportação manual do Timescale

---

## 5. Custo de Reversão

**Baixo** — DuckDB é auxiliar e isolado. Remover do projeto não impacta nenhuma funcionalidade operacional do cockpit.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §6.4 (papel do DuckDB)
- ADRs relacionadas: ADR-004 (Postgres+Timescale — banco primário)
