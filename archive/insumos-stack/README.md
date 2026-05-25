# /archive/insumos-stack — Insumos da síntese de stack

Recomendações técnicas iniciais preservadas como memória histórica. **Não são fonte canônica.**

| Arquivo | Autor | Data | Status |
|---|---|---|---|
| `CLAUDE-STACK-RECOMENDATION.MD` | Claude (Voltaire + Grace) | 2026-05-24 | Insumo da síntese — fundido |
| `GPT-STACK-RECOMENDATION.md` | GPT | 2026-05-24 | Insumo da síntese — fundido |

**Fonte canônica vigente:** [`../../project/STACK-CAM-OFICIAL.md`](../../project/STACK-CAM-OFICIAL.md)

Em caso de divergência entre estes documentos e o STACK-CAM-OFICIAL.md, **prevalece o STACK-CAM-OFICIAL.md**. Estes ficam aqui para auditoria de proveniência das decisões.

## Como a síntese foi feita

O STACK-CAM-OFICIAL.md absorveu:

**Do documento Claude:**

- Estrutura hexagonal do backend (`domain` / `risk` / `strategies` / `execution` / etc.)
- Risk Engine como Pure Python sem I/O, 100% testado com property-based testing
- TimescaleDB como extensão Postgres para tick data
- TradingView Lightweight Charts para candles
- Bot Telegram como canal externo de alerta
- Lista exaustiva de validators do Risk Engine ligada a artigos constitucionais
- Análise de riscos (R1–R8) e mitigações
- Honestidade sobre custos (edge mínimo de sobrevivência)

**Do documento GPT:**

- Filosofia central: "O CaM não substitui o Profit; é cockpit ao redor do Profit"
- Faseamento da integração Profit (manual → CSV → semi-auto → NTSL → APIs)
- SQLite no MVP, Postgres só quando justificar
- DuckDB para analytics em paralelo ao transacional
- Ollama local como opção de IA privada
- ADRs explícitos para cada decisão

**Decisões de meio-termo (não vieram de nenhum dos dois):**

- Risk Engine espelhado em NTSL como segunda linha de defesa (ADR-009)
- Estratégia híbrida de autoridade: Python pré-valida + NTSL executa com regras hard-coded
- Monorepo único `apps/cam-cockpit/{backend,frontend,ntsl}` no MVP
- Dev em Linux + produção em Windows + portabilidade via `pathlib` e adapters injetáveis
