---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-007 — Risk Engine Pure Python no Shared Kernel

> **Data:** 2026-05-24
> **Status:** Aceita
> **Lead:** Oscar · **Cross-cutting:** Kevin (SEC-GOV)
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-007-risk-engine-pure-python-shared-kernel.md`

---

## 1. Contexto

O Risk Engine é a autoridade máxima do CaM (Art. 15º). Toda operação — live, paper trading, backtest — deve passar pelo Risk Engine. A decisão arquitetural sobre onde vive e como é implementado define a confiabilidade de toda a camada de governança.

Duas propriedades são invioláveis:
1. **Autoridade transversal:** o Risk Engine deve ser consultado por TODAS as features que toquem execução — journal, backtest, paper_trading, profit_integration, kill_switch.
2. **Testabilidade determinística:** o Risk Engine deve ser 100% testável de forma isolada, sem dependências de banco, rede, filesystem ou tempo real — apenas lógica pura.

Se o Risk Engine tiver I/O, os testes dependem de mocks frágeis e o módulo pode ser afetado por falhas de infraestrutura durante a validação de uma ordem. Se o Risk Engine viver dentro de uma feature, outras features não podem consultá-lo sem criar acoplamento proibido.

---

## 2. Decisão

O Risk Engine vive em `cam/_shared/risk/` (Shared Kernel) e é implementado como **Python puro sem I/O** (Zero I/O Policy).

**Localização:** `backend/cam/_shared/risk/`

**Interface pública:**
```python
from cam._shared.risk import engine

decision: RiskDecision = engine.validate(
    candidate: OrderCandidate,
    context: RiskContext
)
# RiskDecision = Approved | Rejected(reason: str)
```

**RiskContext** é fornecido pelo chamador (injetado da infraestrutura): contém o estado atual (P&L do dia, posições abertas, fase, DARF status, checklist status, kill switch ativo, etc.). O Risk Engine não faz queries ao banco — recebe tudo no contexto.

**Validators obrigatórios (cobertura 100%):**

| Validator | Artigo Constitucional |
|---|---|
| `max_contracts_check` | Art. 11º — limite absoluto 2 WIN / 2 WDO |
| `phase_contracts_check` | Art. 12º — 1 contrato max em Fase 2; sem simultaneidade |
| `daily_loss_limit_check` | Art. 16º + POV — 3% do capital total |
| `weekly_loss_limit_check` | Art. 16º + POV — 7% |
| `monthly_loss_limit_check` | Art. 16º + POV — 15% (congela fase) |
| `gain_lock_check` | Art. 17º — 2% diário encerra dia |
| `daily_operations_count_check` | Art. 20º + POV — 3 ops (Fase 1-2), 5 ops (Fase 3-4) |
| `martingale_check` | Art. 13º — proíbe aumentar contratos após loss |
| `trading_window_check` | POV — 15min pós-abertura, 10min pré-fechamento, eventos macro |
| `simultaneous_position_check` | Art. 12º + POV — WIN+WDO simultâneo só Fase 3+ |
| `kill_switch_active_check` | Art. 18º — bloqueia tudo se ativo |
| `tax_compliance_check` | Art. 26º — DARF atrasada bloqueia |
| `phase_authorization_check` | Art. 30º — estratégia autorizada na fase atual |
| `pre_market_checklist_check` | Art. 32º — checklist pré-mercado obrigatório |
| `post_market_checklist_check` | Art. 33º — bloqueia próximo pregão se ausente |
| `circuit_breaker_check` | Art. 18º — configurável |
| `setup_a_plus_check` | Art. 11º + Anexo II Fase 4 — 2 contratos só em Setup A+ |

**Testes:**
- `tests/unit/test_risk/`: unitários por validator, nomeados por artigo constitucional
  - Ex: `test_art_11_max_contracts_absolute`, `test_art_15_risk_engine_authority`
- `tests/property/test_risk_invariants/`: property-based via `hypothesis` — gera cenários adversos aleatórios
- Cada artigo constitucional relevante tem pelo menos 1 teste nomeado

**Regra de build (import-linter):**
- `cam/_shared/risk/` NÃO importa de NADA além de stdlib Python
- CI bloqueia merge se `risk/` importar de `features/`, `api/`, `infra/db`, etc.
- Qualquer feature que toque execução DEVE importar `from cam._shared.risk import engine`
- NENHUMA feature duplica lógica de validator

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Risk Engine com I/O (faz queries ao banco dentro do validator) | Quebra testabilidade isolada; validators dependem de infraestrutura; mocks frágeis; falha de banco pode afetar validação de ordem |
| 2 | Risk Engine dentro de uma feature (ex: `features/risk/`) | Features não podem ser importadas por outras features (ADR-013); Risk Engine precisaria estar no Shared Kernel de qualquer forma |
| 3 | Risk Engine duplicado em cada feature | Violação do princípio DRY constitucional; qualquer atualização de regra exigiria alteração em múltiplos lugares; risco de inconsistência entre validators |
| 4 | Risk Engine como serviço HTTP separado (microsserviço) | Over-engineering para cockpit local mono-usuário; latência adicional na validação de ordens; mais pontos de falha |

---

## 4. Consequências

### Positivas
- 100% testável sem mocks de banco ou rede — property-based testing pode gerar cenários adversos ilimitados
- Módulo único de autoridade — não há "dois Risk Engines" que podem divergir
- Pure Python sem I/O = execução em microsegundos — sem latência no caminho crítico de validação
- Import-linter detecta qualquer violação da Zero I/O Policy no CI
- Testes nomeados por artigo constitucional = rastreabilidade direta entre código e lei

### Negativas
- RiskContext precisa ser montado pelo chamador — requer uma camada de serviço que lê o estado atual do banco e monta o contexto antes de chamar o engine
- Validators são stateless — estado (P&L acumulado, operações do dia) deve ser calculado fora do engine e passado no contexto

### Neutras
- A separação RiskContext (estado) × RiskEngine (lógica) é arquiteturalmente limpa, mas requer disciplina para manter atualizado

---

## 5. Custo de Reversão

**Alto** — o Risk Engine é o núcleo constitucional. Mover ou dividir o Risk Engine afeta todas as features que o chamam e toda a camada de testes. Decisão de fundação.

---

## 6. Referências

- Constituição: Arts. 11º–20º, 26º, 30º, 32º, 33º
- DAS: [`../DAS.md`](../DAS.md) §4.1
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §6.3
- ADRs relacionadas: ADR-013 (Shared Kernel mínimo), ADR-009 (NTSL como 2ª linha de defesa)
