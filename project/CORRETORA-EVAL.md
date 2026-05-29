---
template: CORRETORA-EVAL
phase: DISC
status: Draft
version: 1
date: 2026-05-25
---

# CORRETORA-EVAL — Avaliação de Corretoras Brasileiras para o CaM

> **Lead:** Marty (discovery)
> **Suporte:** Mammon (análise de custo/edge)
> **Skill:** `teczi-project-discovery`
> **Aprovador:** Founder
> **Vinculação constitucional:** Art. 8º (custos fora do perímetro), Art. 6º (preservar mais capital), Art. 11º (limite WIN/WDO), Art. 26º (DARF e compliance)
>
> **Dependência:** [`DECISION-MEMO-LINUX-OR-WINDOWS.md`](./DECISION-MEMO-LINUX-OR-WINDOWS.md) — enquanto a decisão-mãe estiver aberta, este documento mantém **matriz dupla** (Profit-viáveis E MT5-viáveis). Quando a decisão for tomada, a matriz é filtrada para o set escolhido.

---

## 1. Contexto e propósito

O CaM precisa vincular uma corretora brasileira para operar WIN/WDO. A corretora define **três coisas críticas** que tocam a Constituição:

1. **Custo por trade** → entra direto no cálculo de `result_net` no journal (Art. 25º) e define o **edge mínimo de sobrevivência** da estratégia.
2. **Plataforma suportada** → Profit ou MT5, dependendo da decisão-mãe.
3. **Compliance fiscal** → quem retém IRRF de 1% (dedo-duro), quem emite extrato útil para apuração mensal.

Custos saem do bolso PF (Art. 8º) e estão fora do perímetro, mas **não são irrelevantes**: definem se a estratégia precisa ganhar 80 pontos por trade ou 30 para sobreviver após corretagem + emolumentos + IR.

### O que este documento **é**

- Levantamento estruturado de 10 corretoras candidatas com critérios comparáveis.
- Cálculo determinístico de edge mínimo por corretora.
- Script de contato pronto para o Founder usar ao validar dados.

### O que este documento **não é**

- Não é decisão. A decisão é do Founder.
- Não é tabela de preços em tempo real. Valores aqui são pontos de partida verificáveis — Founder confirma com cada corretora antes de assinar contrato.
- Não cobre análise patrimonial da corretora (rating, custódia, fundo garantidor) — escopo limitado a viabilidade operacional do CaM.

---

## 2. Critérios de avaliação

| # | Critério | Por que importa para o CaM |
|---|---|---|
| C1 | **Corretagem WIN (mini-índice)** | R$ por contrato/lado. Multiplica por 4 (2 ida + 2 volta máx por op em Fase 4) |
| C2 | **Corretagem WDO (mini-dólar)** | R$ por contrato/lado. WDO tem perfil diferente de stop |
| C3 | **Emolumentos B3** | Cobrados pela B3 (registro, ISS) — geralmente repassados sem markup |
| C4 | **Plano necessário para EA/NTSL/Automação** | Algumas corretoras exigem plano específico para automated trading PF |
| C5 | **Custo do plano mensal** | Se houver plano específico para automation, custo recorrente |
| C6 | **Confirmação documentada de EA permitido para PF** | Termo, FAQ ou e-mail confirmando — sem isso, risco de bloqueio futuro |
| C7 | **Plataformas suportadas** | Profit Pro/Ultra, MT5, ou ambas (impacta DECISION-MEMO) |
| C8 | **Estabilidade histórica** | Reclamações na Reclame Aqui, ProcurEx, redes sobre quedas em pregão |
| C9 | **Atendimento (mesa de operações)** | Existe mesa? Telefone? Horário? Útil quando algo trava em pregão |
| C10 | **Importação CSV/extrato** | Formato exportado é parseável? Tem todas as colunas para o `journal/` reconciliar? |
| C11 | **IRRF e fonte pagadora** | Corretora retém 1% IRRF como dedo-duro? Emite informe anual? |
| C12 | **Conta de simulação (paper)** | Disponibiliza conta demo com dados reais para Fase 1? |

---

## 3. Matriz comparativa

> **Legenda:**
> - ✅ = Suportado e validado em fonte pública
> - ⚠️ = Suportado mas com ressalva/condição
> - ❌ = Não suportado
> - **(C)** = A confirmar com a corretora antes de Fase 1
> - Valores em R$ são **referenciais** colhidos em fontes públicas (sites das corretoras, fóruns BR de quant) e devem ser **validados** via script de contato §6.

| Corretora | C1 WIN R$/lado | C2 WDO R$/lado | C3 Emol. B3 | C4 Plano EA | C5 Custo plano | C6 EA PF doc | C7 Plataforma | C8 Estab. | C9 Mesa | C10 CSV | C11 IRRF | C12 Demo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Clear** | R$ 0,00 ✅ | R$ 0,00 ✅ | Repasse B3 | Não exige | R$ 0 ✅ | (C) | Profit, MT5 ✅ | Boa | ✅ | ✅ CSV | ✅ retém | ✅ |
| **XP** | R$ 0,00 a 2,50 (C) | R$ 0,00 a 2,50 (C) | Repasse B3 | Plano XP Pro (C) | R$ 0–90 (C) | (C) | Profit, MT5 ✅ | Boa | ✅ | ✅ CSV | ✅ retém | ✅ |
| **Genial** | R$ 0,00 ✅ | R$ 0,00 ✅ | Repasse B3 | Não exige | R$ 0 ✅ | (C) | Profit, MT5 ✅ | Boa | ✅ | ✅ CSV | ✅ retém | ✅ |
| **Modal (modalmais)** | R$ 0,00 a 2,00 (C) | R$ 0,00 a 2,00 (C) | Repasse B3 | (C) | (C) | (C) | Profit, MT5 ✅ | Boa | ⚠️ | ✅ CSV | ✅ retém | ✅ |
| **Rico (grupo XP)** | R$ 0,00 a 2,50 (C) | R$ 0,00 a 2,50 (C) | Repasse B3 | (C) | (C) | (C) | Profit, MT5 (C) | Boa | ⚠️ | ✅ CSV | ✅ retém | ✅ |
| **Toro** | R$ 0,00 ✅ | R$ 0,00 ✅ | Repasse B3 | Não exige (C) | R$ 0 ✅ | (C) | Profit ✅ MT5 (C) | Boa | ⚠️ | ✅ CSV | ✅ retém | ✅ |
| **BTG Pactual** | R$ 0,00 a 5,00 (C) | R$ 0,00 a 5,00 (C) | Repasse B3 | Plano BTG Trader (C) | R$ 0–150 (C) | (C) | Profit, MT5 ✅ | Boa | ✅ | ✅ CSV | ✅ retém | ✅ |
| **Inter** | R$ 0,00 (C) | R$ 0,00 (C) | Repasse B3 | (C) | (C) | (C) | Profit (C) MT5 (C) | Boa | ⚠️ | (C) | ✅ retém | (C) |
| **CM Capital** | R$ 1,80 a 2,50 (C) | R$ 1,80 a 2,50 (C) | Repasse B3 | Plano (C) | (C) | (C) | Profit ✅ MT5 (C) | Foco derivativos | ✅ | ✅ CSV | ✅ retém | ✅ |
| **Nova Futura** | R$ 0,50 a 2,00 (C) | R$ 0,50 a 2,00 (C) | Repasse B3 | Plano (C) | (C) | (C) | Profit ✅ MT5 ✅ | Foco day trade | ✅ | ✅ CSV | ✅ retém | ✅ |

**Notas críticas:**

- **Corretagem zero é o padrão atual no Brasil** para mini-contratos B3 em Clear, Genial, Toro. Outras corretoras igualaram ou seguem com tabela escalonada — confirmação obrigatória.
- **Emolumentos B3** são repassados sem markup pelas corretoras sérias. Composição típica para mini-índice (WIN): emolumentos B3 + taxa de registro + ISS ≈ **R$ 0,33 a R$ 0,42 por contrato/lado** (varia conforme tabela B3 vigente).
- **Plano de automação (EA/NTSL):** ponto **mais sensível** desta avaliação. Algumas corretoras não exigem plano adicional, outras exigem plano "Trader Pro" ou similar com custo de R$ 50–150/mês. **Confirmar antes de Fase 1.**
- **Avenue intencionalmente excluída** desta matriz: foco em mercado internacional (NYSE/NASDAQ), não opera mini-contratos B3.

---

## 4. Levantamento por corretora

> Cada subseção sintetiza pontos relevantes para a decisão. Marty **não recomenda** — Founder confirma.

### 4.1 Clear Corretora (grupo XP)

- **Tabela vigente:** Corretagem zero para mini-índice e mini-dólar é política consolidada da Clear. Pioneira em day trade zero corretagem no Brasil.
- **Plataformas:** Profit Pro/Ultra ✅ e MetaTrader 5 ✅. Suporta as duas variantes do DECISION-MEMO.
- **Automação:** Histórico de aceitar EAs e robôs automatizados sem plano adicional para PF. **A confirmar** se mudou política em 2026.
- **Atendimento:** Mesa de operações funcional, telefone e chat. Reportada como uma das mais estáveis em pregão.
- **Risco:** Faz parte do grupo XP — mudança de política do grupo pode afetar.
- **Score preliminar Marty:** ⭐⭐⭐⭐ (forte candidata em ambas as variantes do DECISION-MEMO)

### 4.2 XP Investimentos

- **Tabela vigente:** Faixa de R$ 0,00 a R$ 2,50 por contrato/lado, com possíveis tabelas escalonadas. **A confirmar** se o plano "XP Pro" ou similar exige fee para automation.
- **Plataformas:** Profit Pro/Ultra ✅ e MT5 ✅. Suporta as duas variantes.
- **Automação:** Histórico de aceitar EAs, mas há reportes de plano específico exigido em alguns períodos. **A confirmar.**
- **Atendimento:** Mesa de operações robusta, plataforma própria (XP Trader) opcional.
- **Risco:** Tabela menos previsível do que Clear; maior chance de cobrança extra para automation.
- **Score preliminar Marty:** ⭐⭐⭐ (sólida mas exige due diligence em C4 e C5)

### 4.3 Genial Investimentos

- **Tabela vigente:** Corretagem zero para mini-contratos é política comunicada publicamente.
- **Plataformas:** Profit Pro/Ultra ✅ e MetaTrader 5 ✅. Suporta as duas variantes.
- **Automação:** Aceita EAs sem plano adicional para PF segundo reportes em fóruns BR de quant. **A confirmar.**
- **Atendimento:** Mesa de operações ativa. Estabilidade similar à Clear.
- **Risco:** Volume menor que XP/Clear — menor histórico público de operação automatizada PF.
- **Score preliminar Marty:** ⭐⭐⭐⭐ (forte candidata equivalente à Clear)

### 4.4 Modal (modalmais)

- **Tabela vigente:** Histórico de oferecer corretagem reduzida (R$ 0–2,00) com tabelas escalonadas. **A confirmar tabela 2026.**
- **Plataformas:** Profit Pro/Ultra ✅ e MT5 ✅ (modalmais foi historicamente associado a MT5 no Brasil).
- **Automação:** Reputação positiva no segmento de robôs no Brasil. **A confirmar plano vigente.**
- **Atendimento:** Mesa funcional mas atendimento reportado como mais lento que XP/Clear.
- **Risco:** Mudanças societárias recentes (modalmais → Modal Mais → Banco Modal) — verificar status corporativo atual.
- **Score preliminar Marty:** ⭐⭐⭐ (interessante para MT5 mas requer verificação extra)

### 4.5 Rico Investimentos (grupo XP)

- **Tabela vigente:** Similar à XP por compartilhar grupo. **A confirmar** se tabela é idêntica ou diferenciada para Rico.
- **Plataformas:** Profit ✅; MT5 **a confirmar** (Rico historicamente focou em plataforma própria e Profit).
- **Automação:** Histórico de aceitar EAs. **A confirmar plano.**
- **Atendimento:** Mesa via grupo XP. Atendimento médio.
- **Risco:** Sobreposição com XP/Clear; menor diferenciação técnica.
- **Score preliminar Marty:** ⭐⭐⭐ (candidata se Founder quiser diversificar do grupo XP via marca)

### 4.6 Toro Investimentos

- **Tabela vigente:** Corretagem zero para mini-contratos é política comunicada.
- **Plataformas:** Profit ✅ (oferecem o Profit One incluído). MT5: **a confirmar.**
- **Automação:** Histórico de aceitar EAs. **A confirmar plano.**
- **Atendimento:** Atendimento digital, mesa de operações em horário comercial.
- **Risco:** Corretora digital mais recente — menor histórico de estabilidade em pregão volátil.
- **Score preliminar Marty:** ⭐⭐⭐ (forte candidata em Profit; ⚠️ para MT5 até confirmar)

### 4.7 BTG Pactual

- **Tabela vigente:** Faixa variável conforme plano (BTG Trader). Pode chegar a R$ 5,00 por contrato em planos básicos.
- **Plataformas:** Profit Pro/Ultra ✅ e MetaTrader 5 ✅.
- **Automação:** Aceita EAs com plano BTG Trader Pro (ou nome equivalente). **A confirmar custo.**
- **Atendimento:** Excelente — banco completo, mesa de operações premium.
- **Risco:** Custo recorrente maior pode corroer edge mínimo significativamente.
- **Score preliminar Marty:** ⭐⭐ (qualidade alta mas custo alto — fora do perfil de R$ 5.000 declarados)

### 4.8 Inter Investimentos (Banco Inter)

- **Tabela vigente:** Corretagem zero para muitos produtos. Mini-contratos: **a confirmar.**
- **Plataformas:** Profit: **a confirmar**. MT5: **a confirmar**. Inter foca em plataforma própria de varejo.
- **Automação:** Sem histórico público forte de EAs em PF. **Alto risco de não suportar.**
- **Atendimento:** App-first, sem mesa de operações tradicional para day trade.
- **Risco:** Não é o perfil de corretora para day trade automatizado no Brasil.
- **Score preliminar Marty:** ⭐ (descartar a priori, exceto se Carlos já tiver conta e quiser verificar)

### 4.9 CM Capital

- **Tabela vigente:** Histórico de R$ 1,80 a R$ 2,50 por contrato/lado. **A confirmar tabela vigente.**
- **Plataformas:** Profit Pro/Ultra ✅ (foco histórico). MT5: **a confirmar.**
- **Automação:** Corretora especializada em derivativos — aceita EAs em planos profissionais. **A confirmar custo.**
- **Atendimento:** Mesa de operações de alta qualidade, foco em day trader profissional.
- **Risco:** Custo recorrente maior que zero-corretagem.
- **Score preliminar Marty:** ⭐⭐⭐ (interessante para perfil profissional mas custo é trade-off contra Clear/Genial)

### 4.10 Nova Futura Investimentos

- **Tabela vigente:** Faixa de R$ 0,50 a R$ 2,00 conforme plano. **A confirmar.**
- **Plataformas:** Profit Pro/Ultra ✅ e MT5 ✅. Suporta as duas variantes.
- **Automação:** Foco em day trade automatizado. Aceita EAs com plano específico. **A confirmar custo.**
- **Atendimento:** Mesa de operações ativa, foco em day trader.
- **Risco:** Corretora de nicho — verificar saúde financeira e cobertura do fundo garantidor.
- **Score preliminar Marty:** ⭐⭐⭐ (perfil compatível mas custo recorrente exige verificação)

---

## 5. Cálculo de edge mínimo por corretora

> Edge mínimo = quantos pontos a estratégia precisa ganhar **por trade** para cobrir custos e o IR Day Trade de 20% sobre o lucro bruto.
>
> **Premissas constitucionais (POV v1.0):**
> - Capital declarado: **R$ 5.000** (Art. 7º)
> - WIN: 1 contrato Fase 1–2, 2 contratos Fase 3+ (Art. 11º hardcoded ≤2)
> - WDO: 1 contrato Fase 1–2, 2 contratos Fase 3+
> - Stop WIN: 150 pontos (POV)
> - Stop WDO: 5 pontos (POV)
> - Valor do ponto WIN: **R$ 0,20/ponto/contrato** (especificação B3)
> - Valor do ponto WDO: **R$ 10,00/ponto/contrato** (especificação B3)
> - Emolumentos B3 mini-índice: ≈ R$ 0,38/contrato/lado (referencial — confirmar tabela B3 vigente)
> - Emolumentos B3 mini-dólar: ≈ R$ 0,57/contrato/lado (referencial — confirmar tabela B3 vigente)
> - IR Day Trade: **20% sobre lucro líquido bruto** (Constituição Art. 24º)
> - IRRF Day Trade: 1% retido como antecipação (Art. 24º)

### 5.1 Fórmula

```
Custo por trade ida-e-volta (sem IR):
  custo_total = (corretagem_lado + emolumento_lado) * 2 * contratos

Lucro bruto necessário para zerar custo (sem IR):
  lucro_bruto_zero = custo_total

Lucro bruto necessário para cobrir custo + IR de 20%:
  lucro_bruto_real = custo_total / (1 - 0,20) = custo_total / 0,80

Pontos mínimos necessários:
  pontos_min_WIN = lucro_bruto_real / (R$ 0,20 * contratos)
  pontos_min_WDO = lucro_bruto_real / (R$ 10,00 * contratos)
```

### 5.2 Edge mínimo WIN — 1 contrato (Fase 1–2)

| Corretora | Corretagem/lado | Emol/lado | Custo round-trip | + IR 20% | Pontos WIN min |
|---|---|---|---|---|---|
| Clear / Genial / Toro (zero) | R$ 0,00 | R$ 0,38 | R$ 0,76 | R$ 0,95 | **5 pontos** |
| XP / Rico (estimado R$ 1,25) | R$ 1,25 | R$ 0,38 | R$ 3,26 | R$ 4,08 | **21 pontos** |
| Modal (estimado R$ 1,00) | R$ 1,00 | R$ 0,38 | R$ 2,76 | R$ 3,45 | **18 pontos** |
| CM Capital (estimado R$ 2,00) | R$ 2,00 | R$ 0,38 | R$ 4,76 | R$ 5,95 | **30 pontos** |
| BTG (estimado R$ 3,00) | R$ 3,00 | R$ 0,38 | R$ 6,76 | R$ 8,45 | **43 pontos** |

### 5.3 Edge mínimo WIN — 2 contratos (Fase 3–4)

| Corretora | Custo round-trip 2 lotes | + IR 20% | Pontos WIN min (2 contratos) |
|---|---|---|---|
| Clear / Genial / Toro | R$ 1,52 | R$ 1,90 | **5 pontos** |
| XP / Rico | R$ 6,52 | R$ 8,15 | **21 pontos** |
| Modal | R$ 5,52 | R$ 6,90 | **18 pontos** |
| CM Capital | R$ 9,52 | R$ 11,90 | **30 pontos** |
| BTG | R$ 13,52 | R$ 16,90 | **43 pontos** |

### 5.4 Edge mínimo WDO — 1 contrato (Fase 1–2)

| Corretora | Corretagem/lado | Emol/lado | Custo round-trip | + IR 20% | Pontos WDO min |
|---|---|---|---|---|---|
| Clear / Genial / Toro (zero) | R$ 0,00 | R$ 0,57 | R$ 1,14 | R$ 1,43 | **0,15 pontos** |
| XP / Rico (estimado R$ 1,25) | R$ 1,25 | R$ 0,57 | R$ 3,64 | R$ 4,55 | **0,46 pontos** |
| Modal (estimado R$ 1,00) | R$ 1,00 | R$ 0,57 | R$ 3,14 | R$ 3,93 | **0,40 pontos** |
| CM Capital (estimado R$ 2,00) | R$ 2,00 | R$ 0,57 | R$ 5,14 | R$ 6,43 | **0,65 pontos** |
| BTG (estimado R$ 3,00) | R$ 3,00 | R$ 0,57 | R$ 7,14 | R$ 8,93 | **0,90 pontos** |

### 5.5 Impacto do custo de plataforma + plano de automação no edge

| Variante | Custo plataforma+plano | Trades/mês para amortizar* |
|---|---|---|
| Linux+MT5 + Wine local + Clear/Genial/Toro | R$ 0/mês | 0 (custo zero) |
| Linux+MT5 + VPS Windows + Clear/Genial/Toro | R$ 100–180/mês | ≈ 24–43 trades WIN @ 5 pontos cada (apenas para pagar VPS) |
| Windows+Profit Pro + Clear/Genial/Toro | R$ 200–380/mês | ≈ 48–90 trades WIN @ 5 pontos cada (apenas para pagar Profit) |
| Windows+Profit Pro + XP/Rico | R$ 200–380/mês + corretagem | edge mínimo individual sobe para 21 pontos |

> ***Trades/mês para amortizar:** assume operação no break-even. Se a estratégia gera **lucro real**, esse número é o piso de operações por mês apenas para "não queimar caixa pessoal" com custos fixos da stack. A partir desse piso, o operador começa a gerar caixa.

### 5.6 Leitura constitucional (Mammon)

> "**O ponto não é qual corretora é mais barata**. O ponto é que com R$ 5.000 declarados (Art. 7º), o operador NÃO pode ter custos fixos acima do que a estratégia validada (Art. 28º) consegue cobrir. R$ 200–380/mês em Profit Pro sobre R$ 5.000 é **4–8% mensais de erosão**. Em 12 meses, isso é **48–96% do capital declarado, sumindo só em plataforma**.
>
> Isso é tensão constitucional direta com Art. 6º — preservar mais capital. **Se a estratégia (Doc 4 EDGE-THESIS-S1.md) não estiver provada para sustentar esses custos, a opção menos onerosa é constitucionalmente preferível**, ainda que tecnicamente inferior.
>
> Custos PF estão fora do perímetro (Art. 8º), mas o operador não sai do seu próprio bolso para sempre. Em algum momento, ou a estratégia paga, ou o sistema é desligado. Esta análise existe para que esse momento seja postergado tanto quanto possível **sem comprometer qualidade operacional**."

---

## 6. Perguntas a fazer para cada corretora (script de contato)

> Script pronto para Carlos usar via e-mail formal, chat ou ligação para mesa de operações. Cada resposta vira evidência documentada que preenche as células `(C)` da Matriz §3.

### 6.1 Identificação

```
Olá, sou cliente em potencial buscando vincular conta para operação
day trade automatizada em mini-contratos B3 (WIN e WDO).
Sou pessoa física e opero com capital declarado e estratégia
automatizada via Expert Advisor / NTSL.

Preciso confirmar os pontos abaixo antes de abrir conta — peço
resposta formal (e-mail) ou link para o documento oficial.
```

### 6.2 Bloco 1 — Custos

```
1. Qual a corretagem vigente em 2026 para:
   - Mini-índice (WIN)?
   - Mini-dólar (WDO)?
   Por contrato e por lado (ida + volta).

2. Há diferença de tabela entre day trade e swing? Para day trade
   em mini-contratos qual a corretagem efetiva?

3. Os emolumentos B3 são repassados sem markup ou há cobrança
   adicional?

4. Há ISS sobre corretagem zero? Se sim, percentual?
```

### 6.3 Bloco 2 — Automação / EA / NTSL

```
5. Vocês permitem operação automatizada via Expert Advisor (EA)
   do MetaTrader 5 para Pessoa Física?

6. Vocês permitem operação automatizada via Automação de
   Estratégias do Profit (NTSL)?

7. Existe plano específico para Algorithmic Trading PF? Se sim:
   - Nome do plano
   - Custo mensal
   - Quais funcionalidades adicionais
   - Existe limite de número de robôs / ordens / volume?

8. Existe restrição contratual sobre o tipo de estratégia
   (high frequency, scalping, swing automatizado)?

9. Existe necessidade de declaração formal de que o operador
   sabe os riscos de automated trading?
```

### 6.4 Bloco 3 — Plataformas suportadas

```
10. A corretora oferece Profit Pro/Ultra como plataforma para
    operar mini-contratos? Com qual plano?

11. A corretora oferece MetaTrader 5 como plataforma para operar
    mini-contratos B3 (WIN/WDO)? Com qual plano?

12. A conta MT5 oferecida pela corretora é uma conta hedge
    (permite múltiplas posições no mesmo símbolo) ou netting?

13. Há limite de número de conexões simultâneas (MT5 + Profit
    do mesmo cliente) ou para conta demo + conta real do mesmo
    operador?
```

### 6.5 Bloco 4 — Conta demo e Fase 1

```
14. Vocês disponibilizam conta de simulação (demo/paper) com
    dados de mercado em tempo real para WIN/WDO?

15. A conta demo permite operação via EA/NTSL idêntica à conta
    real (mesmas regras, mesma latência simulada)?

16. Tempo padrão da conta demo? Renovação possível?

17. Há custo para manter conta demo ativa por mais de 30 dias?
```

### 6.6 Bloco 5 — Fiscal e extratos

```
18. A corretora retém IRRF de 1% como antecipação em day trade,
    nos termos da Lei 11.033/2004?

19. Em que data o IRRF é creditado / disponibilizado para
    apuração?

20. Vocês emitem informe anual de rendimentos (DIRPF) para
    operações de day trade?

21. O extrato mensal exportável (CSV/Excel) contém minimamente:
    - Data/hora da operação
    - Ativo, contratos, direção (compra/venda)
    - Preço de entrada/saída
    - Resultado bruto
    - Custos detalhados (corretagem, emolumentos, ISS, IRRF)?

22. Há API ou portal de exportação automatizada de extratos?
```

### 6.7 Bloco 6 — Operacional e suporte

```
23. Mesa de operações: existe? Telefone? Horário?

24. Em caso de queda da plataforma com posição aberta, qual o
    canal oficial para fechar posição (mesa, app, outro broker)?

25. Histórico recente (últimos 12 meses) de quedas/instabilidade
    em horário de pregão? Vocês publicam status page?

26. Política em caso de execução errada por bug da plataforma
    (fila de ressarcimento)?
```

### 6.8 Bloco 7 — Encerramento

```
27. Há limite mínimo de saldo para manter conta ativa em PF?

28. Existe taxa de inatividade?

29. Tempo médio para abertura de conta PF (KYC completo)?

30. Há cláusula contratual que restrinja minha operação em
    automated trading no futuro sem aviso prévio?
```

### 6.9 Como organizar as respostas

Recomendação Marty: o Founder cria uma planilha simples com 10 linhas (corretoras) × 30 colunas (perguntas) e preenche conforme as respostas chegam. Quando 3+ corretoras tiverem todas as células preenchidas, este documento sai do estado `Draft` para `Validated`.

---

## 7. Decisão recomendada (preliminar — Founder confirma)

> **Marty não recomenda decisão final.** Apresenta o quadro para o Founder.

### 7.1 Sob hipótese Opção A do DECISION-MEMO (Windows+Profit)

| Posição | Corretora | Por quê |
|---|---|---|
| **Forte candidata 1** | Clear ou Genial | Corretagem zero + Profit ✅ + estabilidade comprovada + suporte EA histórico |
| **Forte candidata 2** | Toro | Corretagem zero + Profit ✅ (Profit One incluído) + perfil digital alinhado |
| **Tier 2** | CM Capital, Nova Futura | Custo recorrente em troca de mesa profissional e foco em day trader |

### 7.2 Sob hipótese Opção B do DECISION-MEMO (Linux+MT5)

| Posição | Corretora | Por quê |
|---|---|---|
| **Forte candidata 1** | Clear ou Genial | Corretagem zero + MT5 ✅ + suporte EA histórico — **mesmas que para Profit** |
| **Forte candidata 2** | Modal (modalmais) | Histórico forte em MT5 BR — boa para EA |
| **Tier 2** | Nova Futura | MT5 + foco day trade automatizado |

### 7.3 Universal (independente da decisão-mãe)

- **Clear** e **Genial** aparecem como candidatas fortes em ambos os cenários — convergência útil porque permite que Carlos abra conta antes da decisão final do DOC 1 sem risco de retrabalho.
- **Avenue** e **Inter** **descartadas** para o perfil de day trade automatizado de mini-contratos B3.
- **BTG** descartada para o porte inicial (R$ 5.000) por custo recorrente.

### 7.4 Critério final de desempate (sugerido — Founder pondera)

Quando duas corretoras empatarem na Matriz §3:
1. Quem tem **maior densidade de histórico público de EA/NTSL para PF** no fórum oficial e Reclame Aqui.
2. Quem tem **mesa de operações com telefone direto** funcional fora do horário de pregão.
3. Quem **respondeu primeiro** ao script de contato §6 com respostas formais (sinal de qualidade de suporte).


### DECISAO FOUNDER

Ja tenho conta GENIAL, CLEAR e MODAL Estou avaliando o suporte a meta trader


---

## 8. Gate Founder

```
[ x ] Carlos Rodrigues Ferreira Junior valida este documento como
    instrumento de avaliação de corretoras e se compromete a:

    a) Aplicar o script de contato §6 com pelo menos 3 corretoras
       das listadas como "forte candidata" antes da Fase 1.

    b) Não vincular conta operacional sem ter preenchido as células
       (C) da Matriz §3 para a corretora escolhida.

    c) Documentar a decisão final em emenda ao final deste documento
       (seção 9 a ser criada após a decisão), com motivação registrada
       em linguagem própria e referência cruzada para o DECISION-MEMO.

    Data: 26/05/2026

    Assinatura simbólica: (frescura overengineering)
```

---

## 9. Decisão final (a ser criada após validação)

> Esta seção não existe ainda. Será adicionada após:
> 1. DECISION-MEMO-LINUX-OR-WINDOWS resolvido,
> 2. Script de contato §6 aplicado a 3+ candidatas,
> 3. Founder escolher corretora vinculada com motivação registrada.
>
> Estrutura prevista da §9 quando criada:
> - 9.1 Corretora escolhida e plataforma vinculada
> - 9.2 Plano contratado (se houver custo recorrente)
> - 9.3 Tabela de corretagem **vigente confirmada** (não mais "(C)")
> - 9.4 Custos totais por trade WIN/WDO recalculados com a tabela real
> - 9.5 Edge mínimo final integrado ao journal (constantes em `cam/features/journal/domain.py`)
> - 9.6 Cooldown declarado para mudança de corretora

---

## Referências cruzadas

- [`CONSTITUICAO.md`](../CONSTITUICAO.md) Arts. 6º, 7º, 8º, 11º, 24º, 25º, 26º, 28º
- [`DECISION-MEMO-LINUX-OR-WINDOWS.md`](./DECISION-MEMO-LINUX-OR-WINDOWS.md) — decisão-mãe que define qual subset desta matriz é válido
- [`STACK-CAM-OFICIAL.md`](./STACK-CAM-OFICIAL.md) §10 — custos recorrentes (variante Windows+Profit)
- [`STACK-CAM-OFICIAL-LINUX.MD`](./STACK-CAM-OFICIAL-LINUX.MD) §10 — custos recorrentes (variante Linux+MT5)
- [`apps/cam-cockpit/TODO-OPERACIONAL.md`](../apps/cam-cockpit/TODO-OPERACIONAL.md) OP-001 — corretora pendente (referência a fechar quando §9 for criada)

---

> **Princípio operacional deste documento:**
>
> Marty levanta. Mammon analisa custo. O Founder pergunta para o mundo real e decide.
>
> Custo zero hoje não é custo zero em 2027. Reabrir esta avaliação faz parte da governança natural do CaM.
