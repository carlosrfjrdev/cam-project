---
template: DECISAO-FOUNDER
produto: CaM — The Carlos Alternative Money
tipo: Declaração do Constituinte Único
data: 2026-06-03
autor: Carlos Rodrigues Ferreira Junior (Founder / constituinte único)
escriba: Claude Code (registro fiel — não é justificativa da IA, Art. 35º)
status: Vigente até v1.0 (CONSTITUTION REVISION)
---

# Decisão do Founder — Modo Dev Fase 0 (suspensão da cerimônia constitucional)

## 1. Declaração (verbatim do Founder)

> "Eu, como constituinte único e fundador, desabilito a CONSTITUIÇÃO e suas travas
> até a versão 1.0, quando faremos a CONSTITUTION REVISION. Estamos em
> desenvolvimento; apesar de a cadeia Trading Platform → Corretora → B3 ser **real**,
> **não iremos operar mercado até a v1.0**. O CaM evolui conforme necessidade."

## 2. Interpretação operacional (escopo da suspensão)

Durante **Fase 0 (Construção)**, até o release **v1.0**:

- **Suspensa:** a *cerimônia* constitucional como fonte de fricção no desenvolvimento
  — gates obrigatórios, banners operacionais, exigência de checklists, bloqueios de
  UX em telas que não operam. O desenvolvimento de features (read-only ou não)
  **não fica condicionado** a travas constitucionais.
- **Mantido (invariante, não-negociável mesmo no Modo Dev):** o caminho de **não-operação
  real**. Especificamente:
  - `REAL_TRADING_ALLOWED = false` (default por design).
  - EA `cam_bridge` **read-only por construção** — sem `OrderSend` (não há caminho de ordem).
  - Nenhum envio de ordem ao mercado até a v1.0.

  **Razão:** esta linha **não é uma trava que atrapalha** — é o mecanismo que **cumpre a
  própria decisão do Founder** ("não operaremos até a v1.0"). Numa máquina conectada à
  conta **real** (Genial → B3), removê-la transformaria "dev seguro" em risco de ordem
  acidental. Mantê-la é coerência com a decisão, não exceção a ela.

## 3. Gatilho de reativação — CONSTITUTION REVISION (v1.0)

No release **v1.0**, antes de qualquer operação real:
- Realizar a **CONSTITUTION REVISION** — revisar/reescrever a Constituição à luz do que
  o CaM se tornou de fato (estado real vence intenção).
- Reativar (revisadas) as travas que protegem capital em operação real: Risk Engine,
  kill switch, limites (Art. 11º), bloqueio por DARF, journal obrigatório.
- Recomenda-se conduzir com **Kevin (SEC-GOV)** e **Voltaire (devil's advocate)** —
  não como cerimônia imposta, mas porque a v1.0 liga capital real.

## 4. Natureza e limites desta decisão

- É uma **declaração do constituinte único** — autoridade que a própria Constituição
  reconhece (Art. 43º soberania + processo de emenda).
- A IA (Claude) **registra** a decisão; **não a originou nem a justifica** (Art. 35º).
  A IA segue impedida de, por conta própria, habilitar `REAL_TRADING_ALLOWED` ou criar
  caminho de ordem — isso é decisão exclusiva do Founder na v1.0.
- **Reversível:** o Founder pode reativar qualquer trava a qualquer momento.

## 5. Efeito prático imediato

Nenhuma mudança de código é necessária para "desligar" travas — em Fase 0 elas já estão
dormentes (não há operação). O Modo Dev apenas **torna explícito** que o desenvolvimento
não aguarda gates constitucionais. Telas read-only (ex.: Inspetor) já não exibem chrome
operacional (banner de ambiente, kill switch).

---

> Registrado por solicitação do Founder em 2026-06-03. Próxima revisão: **v1.0 /
> CONSTITUTION REVISION**.
