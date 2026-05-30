---
template: ADR
phase: ARCH
status: Superseded-in-part
---

# ADR-009 — Risk Engine Espelhado em ~~NTSL~~ **MQL5** como Segunda Linha de Defesa

> ⚠️ **ATUALIZADA (soft-stage, 2026-05-30).** O espelho de risco é implementado em
> **MQL5**, não NTSL: **`apps/cam-cockpit/mql5/experts/cam_risk_mirror.mq5`** — o
> ÚNICO arquivo autorizado a `OrderSend` (allowlist enforçada por
> `scripts/lint_mql5.py`), que entrega **só em conta DEMO**. O **princípio
> permanece intacto**: regras de risco não-negociáveis espelhadas no broker como
> segunda linha de defesa hard-coded (Arts. 15º/18º/19º). Releia "NTSL" → MQL5;
> "estratégia NTSL no Profit" → EA no MT5. Soft-stage (pré-v1) — sem ADR HARD.
> SSoT: [`../../STACK-CAM-OFICIAL.md`](../../STACK-CAM-OFICIAL.md).

> **Data:** 2026-05-24 · **Atualizada:** 2026-05-30
> **Status:** Superseded-in-part (princípio mantido; espelho = MQL5 cam_risk_mirror.mq5)
> **Lead:** Oscar · **Cross-cutting:** Kevin (SEC-GOV)
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-009-risk-ntsl-segunda-linha-defesa.md`

---

## 1. Contexto

O Risk Engine Python (`cam/_shared/risk/`) é a **autoridade primária** de validação (Art. 15º). Quando o CaM avançar para a Fase F4 de integração (NTSL com execução automática no Profit), o Risk Engine Python atua como pré-validador antes de autorizar a estratégia NTSL a executar.

Contudo, em cenários de falha técnica (backend Python indisponível, rede local comprometida, travamento do processo), a estratégia NTSL no Profit pode continuar recebendo sinais de mercado e tentar executar sem passar pelo Risk Engine Python.

A Constituição é explícita: falha técnica não justifica operação fora de regra. Art. 19º: "posição aberta sem cobertura sistêmica é risco inaceitável". Art. 18º: kill switch deve ser acionável por "falha técnica".

---

## 2. Decisão

As **regras de risco mecânico não-negociáveis** da Constituição são **espelhadas em NTSL** dentro das estratégias como **segunda linha de defesa hard-coded**.

**O que vai para o NTSL:**
- Limite absoluto de contratos: `if (nContracts > 2) then exit; // Art. 11`
- Verificação de janelas vedadas (horário): pós-abertura 15min, pré-fechamento 10min
- Stop loss mínimo hard-coded por ativo (WIN: 150p mínimo; WDO: 3p mínimo)
- Verificação de kill switch via variável publicada pelo CaM backend (parâmetro lido pela estratégia)

**O que NÃO vai para o NTSL:**
- Lógica de P&L acumulado do dia (NTSL não tem acesso ao banco do CaM)
- Verificação de DARF (estado fiscal — NTSL não conhece o ledger)
- Cálculo complexo de drawdown semanal/mensal (requer histórico persistido)
- Toda lógica que depende de estado armazenado fora do Profit

**Publicação de parâmetros:** o CaM backend (`features/profit_integration/ntsl_publisher.py`) publica os parâmetros vigentes (fase atual, kill switch ativo, Stop A+ autorizado) em arquivo/variável que a estratégia NTSL lê no início de cada pregão.

**Testes de paridade NTSL↔Python:** para cada cenário canônico (limite de contratos, janelas vedadas, stops padrão), há teste que verifica que NTSL e Python tomam a mesma decisão.

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Somente Risk Engine Python (sem NTSL espelhada) | Se backend Python cair com posição aberta, NTSL continua operando sem controle algum — risco inaceitável (Art. 19º) |
| 2 | NTSL com toda a lógica do Risk Engine | NTSL não tem acesso a estado externo (banco, ledger, aderência histórica) — impossível espelhar completamente; manutenção de lógica complexa em duas linguagens distintas |
| 3 | Kill switch físico (desligar o Profit) | É um last resort — Art. 18º prevê kill switch digital primeiro; desligar o Profit é intervenção manual de emergência, não proteção sistêmica automática |

---

## 4. Consequências

### Positivas
- Proteção em camadas: mesmo se o backend Python falhar, os limites hard-coded em NTSL impedem as piores violações
- Kill switch propagado via parâmetro: backend ativa kill switch, NTSL para de executar no próximo ciclo
- Reduz superfície de desastre em falha técnica parcial (Art. 19º)

### Negativas
- Manutenção em duas linguagens (Python e NTSL): toda mudança em regra hard-coded de risco precisa ser sincronizada
- Risco de divergência entre NTSL e Python se sincronização falhar (mitigado por testes de paridade)
- NTSL é linguagem proprietária Nelogica — debugging e testes são mais limitados que Python

### Neutras
- A NTSL espelhada não replica toda a riqueza do Risk Engine Python — apenas as regras mais críticas que podem ser implementadas sem estado externo

---

## 5. Custo de Reversão

**Médio** — remover a espelhagem NTSL enfraquece a defesa em camadas. Adicionar de volta requer reescrever a lógica em NTSL e criar testes de paridade. Não é uma decisão que se reverte facilmente pós-Fase F4.

---

## 6. Referências

- Constituição: Arts. 11º, 15º, 18º, 19º
- DAS: [`../DAS.md`](../DAS.md)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §2 (Princípio 10)
- ADRs relacionadas: ADR-001 (Profit como plataforma), ADR-007 (Risk Engine primário), ADR-008 (integração faseada)
