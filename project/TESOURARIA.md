---
template: TESOURARIA
phase: SDOC
status: Draft
version: 1
date: 2026-05-25
---

# TESOURARIA — Dinâmica de Capital dos 3 Buckets do CaM

> **Lead:** Mammon (capital, dinheiro)
> **Suporte:** Denis (documentação)
> **Skill:** `teczi-software-documentation`
> **Aprovador:** Founder
> **Vinculação constitucional:** Arts. 10º (3 buckets), 21º (Harvest), 22º (Sangria), 23º (Carteira Hard)
>
> **Propósito:** Documento narrativo + tabelas explicando o **estado e a dinâmica** dos 3 buckets do CaM. Útil para Carlos conferir manualmente o capital enquanto o cockpit ainda não exibe o dashboard de tesouraria; útil para a UI quando ela estiver pronta como referência de comportamento esperado.

---

## 1. Princípio

O capital do CaM é **segregado em 3 buckets** com propósitos distintos. **Cada bucket tem regras próprias de entrada, saída, crescimento e encolhimento.** Misturar é violar Art. 10º.

### Os 3 buckets

```
┌─────────────────────────────────────────────────────────────┐
│                  CaM — Capital Total: R$ 5.000              │
├──────────────────┬──────────────────┬──────────────────────┤
│  Bucket          │  Buffer          │  Carteira Hard       │
│  Derivativo      │  Operacional     │  Inicial             │
│  R$ 3.000        │  R$ 1.000        │  R$ 1.000            │
│  60%             │  20%             │  20%                 │
└──────────────────┴──────────────────┴──────────────────────┘
       ↓                  ↓                    ↓
   Opera WIN/WDO       NÃO opera          Aquisição de
   (capital de risco)  (reserva técnica)  ativos longo prazo
```

### Princípio de não-contaminação

| Fluxo | Permitido? | Origem |
|---|---|---|
| Derivativo → Carteira Hard (via Sangria) | ✅ | Art. 22º |
| Buffer → Derivativo (reposição de perda) | ❌ | Art. 10º (Buffer NÃO opera) |
| Carteira Hard → Derivativo (cobertura de erro) | ❌ | Art. 23º |
| Lucro do dia → Buckets (via Harvest) | ✅ | Art. 21º (mensal pós-DARF) |
| Aporte externo → qualquer bucket | ⚠️ | Art. 9º — só com revisão formal de fase |

---

## 2. Estado inicial (snapshot ao iniciar)

Conforme Art. 10º + Anexo III POV v1.0:

| Bucket | Valor | Origem |
|---|---:|---|
| **Bucket Derivativo** | R$ 3.000,00 | Aporte inicial do operador (PF) |
| **Buffer Operacional** | R$ 1.000,00 | Aporte inicial do operador (PF) |
| **Carteira Hard Inicial** | R$ 1.000,00 | Aporte inicial do operador (PF) |
| **TOTAL** | **R$ 5.000,00** | Capital declarado (Art. 7º) |

### Snapshot inicial em SQL

```sql
INSERT INTO cam_bucket_transactions (id, bucket, kind, amount, balance_after, note, created_at)
VALUES
  (gen_random_uuid(), 'BUCKET_DERIVATIVO', 'INITIAL_DEPOSIT', 3000.00, 3000.00, 'Aporte inicial Art. 10º', NOW()),
  (gen_random_uuid(), 'BUFFER_OPERACIONAL', 'INITIAL_DEPOSIT', 1000.00, 1000.00, 'Aporte inicial Art. 10º', NOW()),
  (gen_random_uuid(), 'CARTEIRA_HARD',     'INITIAL_DEPOSIT', 1000.00, 1000.00, 'Aporte inicial Art. 10º', NOW());
```

> **Tarefa pendente (TODO):** abrir TD para seed inicial no migration ou em script de inicialização (`scripts/seed_initial_buckets.py`).

---

## 3. Definição e propósito de cada bucket

### 3.1 Bucket Derivativo

| Campo | Valor |
|---|---|
| **Definição** | Capital de risco operacional destinado **exclusivamente** à operação de mini-índice (WIN) e mini-dólar (WDO) |
| **Linha de base** | R$ 3.000,00 |
| **Quem aporta** | Sangria reversa (não existe — bucket nunca cresce além do teto sem violação) |
| **Quem retira** | Sangria automática quando atinge R$ 4.500 (150% do base — Art. 22º) |
| **Quando cresce** | Lucro tático diário, antes do harvest mensal |
| **Quando encolhe** | Perdas operacionais até o limite de loss (Art. 16º) |
| **Teto operacional** | R$ 4.500 — dispara Sangria automática (Art. 22º) |
| **Piso teórico** | R$ 0 (mas Art. 16º bloqueia operação muito antes de zerar) |

**Por que esse bucket existe:** Para **isolar** o risco operacional do patrimônio. Se a operação tática quebrar, **só o Bucket Derivativo é afetado**. Buffer e Carteira Hard permanecem intocados.

### 3.2 Buffer Operacional

| Campo | Valor |
|---|---|
| **Definição** | Reserva técnica destinada a absorver eventos extremos e cobrir provisão fiscal. **NÃO opera.** |
| **Linha de base** | R$ 1.000,00 |
| **Quem aporta** | Harvest mensal (40% do lucro líquido até completar R$ 1.000) + Sangria (20% do excedente) |
| **Quem retira** | Cobertura de provisão fiscal se DARF mensal > saldo de IR no Bucket Derivativo |
| **Quando cresce** | Harvest e Sangria; até o limite de R$ 1.000 (linha de base) |
| **Quando encolhe** | Pagamento de DARF se Bucket Derivativo não cobrir |
| **Teto** | Quando o Buffer está em R$ 1.000, 100% do harvest passa a ir para Carteira Hard |
| **Piso operacional** | Se < R$ 500, sinal de alerta — provisão fiscal pode estar em risco |

**Por que esse bucket existe:** Para **garantir** que a obrigação fiscal seja paga independentemente do resultado operacional. DARF é compliance não-negociável (Art. 26º).

### 3.3 Carteira Hard

| Campo | Valor |
|---|---|
| **Definição** | Núcleo patrimonial. Contém ativos de longo prazo (ações de dividendo, FIIs) acumulados a partir de lucro operacional do CaM |
| **Linha de base** | R$ 1.000,00 (capital inicial alocado para primeira aquisição) |
| **Quem aporta** | Harvest mensal (60% do lucro líquido) + Sangria (80% do excedente do Derivativo) |
| **Quem retira** | **Ninguém** — Carteira Hard nunca é vendida para cobrir erro operacional (Art. 23º) |
| **Quando cresce** | Continuamente via Harvest e Sangria |
| **Quando encolhe** | Apenas em evento patrimonial externo (venda voluntária do operador, fora do escopo do CaM) |
| **Teto** | Sem teto — é o destino final do capital |

**Por que esse bucket existe:** Para **converter ganhos táticos em patrimônio**. Trade gera renda variável; Carteira Hard gera dividendos passivos. O CaM existe para fazer essa conversão acontecer (Art. 1º + Art. 21º).

---

## 4. Dinâmica entre buckets

### 4.1 Sangria (Derivativo → Carteira Hard + Buffer)

> **Disparo automático** quando Bucket Derivativo atinge R$ 4.500.

```
Antes:
  Bucket Derivativo: R$ 4.500  (atingiu 150% do base)
  Buffer Operacional: R$ X
  Carteira Hard:     R$ Y

Sangria (excedente R$ 1.500 distribuído):
  → 80% = R$ 1.200  →  Carteira Hard
  → 20% = R$ 300    →  Buffer (ou provisão fiscal)

Depois:
  Bucket Derivativo: R$ 3.000  (retorna ao base)
  Buffer Operacional: R$ X + 300
  Carteira Hard:     R$ Y + 1.200
```

**Princípio:** O motor especulativo **nunca cresce de forma ilimitada**. O lucro vira patrimônio, não alavancagem.

### 4.2 Harvest (Lucro líquido mensal → Carteira Hard + Buffer)

> **Disparo manual mensal** após apuração e pagamento de DARF.

```
Pré-condição: DARF do mês anterior PAGA (Art. 26º).

Cálculo do lucro líquido mensal:
  lucro_bruto_mes - custos - IR_20% = lucro_liquido_distribuivel

Distribuição:
  Se Buffer < R$ 1.000 (precisa completar):
    → 60% × lucro_liquido  →  Carteira Hard
    → 40% × lucro_liquido  →  Buffer (até atingir R$ 1.000)
    → Excedente do 40% (se atingiu R$ 1.000 antes de esgotar)  →  Carteira Hard

  Se Buffer ≥ R$ 1.000 (já completo):
    → 100% × lucro_liquido  →  Carteira Hard
```

**Janela de execução:** **mensal** pós-apuração fiscal, **não** diariamente (Art. 21º — evita fricção tributária).

**Aprovação:** Gate Founder obrigatório (SPEC R4.07). Cockpit propõe; Founder executa.

### 4.3 Reposição do Buffer (regra crítica)

> O Buffer **NÃO PODE** ser reposto com **aporte externo** vindo do PF.

Reposição válida (origens permitidas):
- ✅ Harvest mensal (40% do lucro até linha de base).
- ✅ Sangria (20% do excedente do Derivativo).

Reposição inválida (origens proibidas):
- ❌ Transferência do operador para repor depois de pagamento extraordinário de DARF (viola Art. 9º — aporte externo só com revisão formal de fase).
- ❌ Transferência do Bucket Derivativo (Buffer NÃO opera — Art. 10º).
- ❌ Venda de ativo da Carteira Hard (Art. 23º).

> **Implicação:** se o Buffer cair abaixo de R$ 500 e não houver Harvest nem Sangria recente, **o operador está rodando com proteção fiscal fragilizada**. Sinal de alerta.

---

## 5. Cenários exemplificativos com números

### 5.1 Cenário positivo — mês com lucro

**Mês X — Janeiro 2027 (hipotético):**

```
Estado inicial:
  Bucket Derivativo:  R$ 3.000
  Buffer Operacional: R$ 1.000  (já completo)
  Carteira Hard:      R$ 1.000
  TOTAL:              R$ 5.000

Operações do mês: 30 trades
  - Lucro bruto:      R$ 800
  - Custos:           R$ 50
  - IR (20% s/ 750):  R$ 150
  - IRRF retido (1% bruto): R$ 8 (já abatido do DARF)
  - DARF a pagar:     R$ 142
  - Lucro LÍQUIDO mensal: R$ 600

Estado pós-operação (antes do Harvest):
  Bucket Derivativo:  R$ 3.000 + R$ 750 (lucro pós-IR) = R$ 3.750
  Buffer Operacional: R$ 1.000
  Carteira Hard:      R$ 1.000
  IR provisionado:    R$ 150 (separado conceitualmente no Bucket Derivativo)

DARF pago: -R$ 142 do Bucket Derivativo
  Bucket Derivativo: R$ 3.750 - R$ 142 = R$ 3.608

Harvest (1º dia útil do mês seguinte, R$ 600 distribuível):
  Buffer já está em R$ 1.000 — Harvest 100% para Carteira Hard
  → R$ 600 para Carteira Hard

Estado final pós-Harvest:
  Bucket Derivativo:  R$ 3.608
  Buffer Operacional: R$ 1.000
  Carteira Hard:      R$ 1.600
  TOTAL:              R$ 6.208
```

**Observações:**
- O Bucket Derivativo cresceu mesmo após o Harvest porque o lucro foi superior ao excedente do Harvest.
- A Carteira Hard cresceu 60% (de R$ 1.000 para R$ 1.600) em um único mês positivo.
- O Buffer permanece em R$ 1.000 (já está na linha de base).

### 5.2 Cenário negativo — mês com prejuízo dentro do limite

**Mês Y — Fevereiro 2027 (hipotético):**

```
Estado inicial (vindo de janeiro):
  Bucket Derivativo:  R$ 3.608
  Buffer Operacional: R$ 1.000
  Carteira Hard:      R$ 1.600
  TOTAL:              R$ 6.208

Operações do mês: 25 trades
  - Resultado bruto: -R$ 400 (prejuízo)
  - Custos:          R$ 40
  - IR:              R$ 0 (loss não gera IR)
  - Loss compensável acumulado: R$ 440

Estado pós-operação:
  Bucket Derivativo: R$ 3.608 - R$ 440 = R$ 3.168
  Buffer Operacional: R$ 1.000  (intocado)
  Carteira Hard:      R$ 1.600  (intocado)

Harvest do mês: NÃO HÁ (lucro líquido = 0)

Estado final:
  Bucket Derivativo:  R$ 3.168
  Buffer Operacional: R$ 1.000
  Carteira Hard:      R$ 1.600
  TOTAL:              R$ 5.768

Compensação de prejuízo (Art. 27º): R$ 440 disponível para compensar
lucros futuros em day trade. Registrado em `cam_loss_compensation_ledger`.
```

**Observações:**
- Mês negativo afetou **apenas** o Bucket Derivativo. Buffer e Carteira Hard ficaram protegidos por design (Art. 10º).
- O prejuízo de R$ 440 é compensável em meses futuros — não some, fica em ledger.
- Total caiu R$ 440 porque a perda foi real, mas o **patrimônio acumulado (Carteira Hard)** permaneceu intacto.

### 5.3 Cenário catastrófico — mês com loss limit atingido

**Mês Z — Março 2027 (hipotético):**

```
Estado inicial:
  Bucket Derivativo:  R$ 3.168
  Buffer Operacional: R$ 1.000
  Carteira Hard:      R$ 1.600
  TOTAL:              R$ 5.768

Operações: limite mensal atingido (-15% sobre capital total declarado de R$ 5.000)
  - Loss limit mensal: R$ 750 (R$ 5.000 × 15%)
  - O CaM CONGELA a fase atual (Art. 16º + Anexo II)
  - Retorna à fase anterior com revisão formal

Estado pós-operação:
  Bucket Derivativo: R$ 3.168 - R$ 750 = R$ 2.418
  Buffer Operacional: R$ 1.000  (intocado)
  Carteira Hard:      R$ 1.600  (intocado)

Harvest do mês: NÃO HÁ.

Estado final:
  Bucket Derivativo:  R$ 2.418  (não há reposição — não pode operar)
  Buffer Operacional: R$ 1.000
  Carteira Hard:      R$ 1.600
  TOTAL:              R$ 5.018

Loss compensável total: R$ 440 (de Fev) + R$ 750 (de Mar) = R$ 1.190
```

**Observações:**
- **A fase foi congelada.** Não é mais sobre rebuilding capital — é sobre review.
- Buffer e Carteira Hard permaneceram **intocados pelo design**. Mesmo no pior mês, o patrimônio acumulado não foi sacrificado.
- O total caiu apenas R$ 750 do mês (perda) — a **Carteira Hard atua como almofada patrimonial**.
- Após revisão formal, o operador pode optar por:
  - Retornar à fase anterior e reconstruir capital de risco.
  - Reduzir exposição operacional (POV alterada).
  - Pausar trade por período definido.

### 5.4 Cenário de sangria — Bucket Derivativo atinge R$ 4.500

**Mês W (hipotético, vários meses positivos seguidos):**

```
Estado pré-sangria:
  Bucket Derivativo:  R$ 4.500  (atingiu disparo R$ 4.500)
  Buffer Operacional: R$ 1.000
  Carteira Hard:      R$ 2.500
  TOTAL:              R$ 8.000

Sangria automática disparada:
  Excedente: R$ 1.500
  → 80% (R$ 1.200) para Carteira Hard
  → 20% (R$ 300) para Buffer
    (Buffer está em R$ 1.000 — já cheio; R$ 300 vão para provisão fiscal/Buffer)

Estado pós-sangria:
  Bucket Derivativo: R$ 3.000  (retornou ao base)
  Buffer Operacional: R$ 1.000  (já estava cheio — R$ 300 podem ir para outro fim ou ficar como cushion temporário)
  Carteira Hard:      R$ 3.700  (cresceu R$ 1.200)
  TOTAL:              R$ 7.700  (perdeu R$ 300 do TOTAL porque foi para provisão extra)
```

**Observações:**
- A **catraca constitucional** funcionou: o motor especulativo voltou ao tamanho-base; o excedente virou patrimônio (80%) e cushion fiscal (20%).
- A Carteira Hard ficou 270% maior que a inicial (de R$ 1.000 para R$ 3.700) em poucos meses positivos.
- O total efetivo cresceu mesmo após a sangria (R$ 5.000 → R$ 7.700).

---

## 6. Restrições constitucionais sobre movimentação entre buckets

| Restrição | Origem | Consequência se violada |
|---|---|---|
| Bucket Derivativo nunca opera além de R$ 4.500 sem Sangria | Art. 22º | Risk Engine bloqueia (futuro); por enquanto, sinal de alerta |
| Buffer Operacional não opera nunca | Art. 10º | Acesso ao Buffer para operação = violação direta — kill switch imediato |
| Carteira Hard não cobre erro operacional | Art. 23º | Venda de ativos da Carteira Hard para repor Bucket Derivativo é **proibida** |
| Harvest só após DARF paga | Art. 21º + Art. 26º | Harvest sem DARF paga é violação fiscal + operacional |
| Aporte externo só com revisão formal de fase | Art. 9º | Aporte para "ajustar" o capital após loss é proibido (anti-padrão emocional) |
| Setup A+ só após Fase 3 + critério escrito em POV | Art. 11º + Glossário | 2 contratos sem Setup A+ definido = violação Art. 11º |

---

## 7. Como o operador usa este documento

> **Antes do cockpit estar pronto:**
>
> Carlos usa esta tesouraria como **planilha de referência**. Cada mês:
> 1. Recalcula manualmente o estado dos 3 buckets.
> 2. Verifica se atingiu o disparo de Sangria (R$ 4.500 no Bucket Derivativo).
> 3. Decide sobre Harvest (gate manual após DARF paga).
> 4. Registra em journal qualquer movimentação.
>
> **Depois do cockpit estar pronto:**
>
> A UI `/harvest` e `/carteira-hard` exibem os snapshots em tempo real. Este documento serve como:
> - **Onboarding** para validar que a UI está exibindo corretamente.
> - **Especificação de comportamento** para Linus em QA.
> - **Auditoria histórica** se houver dúvida sobre regra aplicada.

---

## 8. Gate Founder

```
[ ] Carlos Rodrigues Ferreira Junior reconhece que:

    a) A separação dos 3 buckets é constitucional e inviolável
       (Art. 10º).

    b) Os 4 cenários de §5 representam a dinâmica esperada do CaM
       e são fidedignos à Constituição + POV vigente.

    c) Movimentação manual entre buckets é proibida fora dos
       fluxos formais (Harvest + Sangria).

    d) Este documento será a referência de comportamento esperado
       quando a UI de tesouraria estiver pronta (painéis Harvest
       e Carteira Hard).

    Data: ___/___/______

    Assinatura simbólica: _________________________
```

---

## Referências cruzadas

- [`CONSTITUICAO.md`](../CONSTITUICAO.md) Arts. 7º, 8º, 9º, 10º, 16º, 21º, 22º, 23º, 26º, 27º
- [`POV-VIGENTE-v1.0.md`](./POV-VIGENTE-v1.0.md) §3.7 Harvest, §3.8 Sangria
- [`apps/cam-cockpit/backend/cam/features/harvest/`](../apps/cam-cockpit/backend/cam/features/harvest/) — service de Harvest e Sangria
- [`apps/cam-cockpit/backend/cam/features/ledger/`](../apps/cam-cockpit/backend/cam/features/ledger/) — buckets em código
- [`apps/cam-cockpit/backend/cam/features/fiscal/`](../apps/cam-cockpit/backend/cam/features/fiscal/) — DARF + compensação de prejuízo
- [`apps/cam-cockpit/frontend/src/features/harvest/HarvestPage.tsx`](../apps/cam-cockpit/frontend/src/features/harvest/HarvestPage.tsx) — UI Harvest
- [`apps/cam-cockpit/frontend/src/features/carteira-hard/CarteiraHardPage.tsx`](../apps/cam-cockpit/frontend/src/features/carteira-hard/CarteiraHardPage.tsx) — UI Carteira Hard

---

> **Princípio operacional deste documento:**
>
> Mammon mede o dinheiro. Denis documenta o caminho.
>
> O motor especulativo nunca cresce além do teto. O patrimônio nunca diminui por erro operacional. **A catraca é constitucional.**
