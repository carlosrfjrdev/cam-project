---
template: ADR
phase: ARCH
status: Under-evaluation
---

# ADR-016 — Plataforma de Execução: **MetaTrader 5 em avaliação · Profit em standby**

> ℹ️ *Renumerado de ADR-001 → ADR-016 em 2026-06-30 (reorg A3) para resolver a
> colisão com o ADR-001 (repo-wide) de personas. Conteúdo inalterado.*

> ⚠️ **EM REAVALIAÇÃO (soft-stage, 2026-05-30).** A escolha de broker está **em
> aberto**. Estado atual:
> - **SO firme:** Windows 11 (o MT5 sob Wine no Linux falhou — isso está decidido).
> - **MetaTrader 5:** em **avaliação ativa** no Windows (Founder já criou alguns
>   pontos/setups). É o caminho em teste primeiro.
> - **Profit/Nelogica:** **NÃO foi descartado** — está em **STANDBY**, mantido como
>   opção até o **primeiro teste** do MT5 validar (ou não) a migração.
>
> **Decisão de broker pendente do primeiro teste.** Soft-stage (pré-v1) — sem ADR
> HARD; nada aqui é irreversível. O texto abaixo (Profit como padrão) permanece
> válido como racional do Profit enquanto ele estiver em standby.
> SSoT da stack: [`../../STACK-CAM-OFICIAL.md`](../../STACK-CAM-OFICIAL.md).

> **Data:** 2026-05-24 · **Reavaliação:** 2026-05-30
> **Status:** Under-evaluation (MT5 em teste · Profit em standby · decide após 1º teste)
> **Lead:** Oscar
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/tcam/adrs/ADR-016-plataforma-execucao.md`

---

## 1. Contexto

Carlos opera mini índice WIN e mini dólar WDO na B3. A plataforma Profit Pro/Ultra da Nelogica é o padrão do mercado brasileiro para trader pessoa física com acesso direto ao book de ofertas, integração com corretoras B3, suporte a automação via NTSL (Nelogica Trading System Language) e, futuramente, módulo de Automação de Estratégias para conta real.

O CaM precisa definir qual plataforma é a autoridade de execução. Há alternativa (MetaTrader 5 + variante Linux) documentada em `STACK-CAM-OFICIAL-LINUX.MD`, mas a decisão deve ser tomada antes de construir a infraestrutura de integração.

Restrição fundamental: a plataforma de execução deve ser Windows-compatible (Profit é Windows-only).

---

## 2. Decisão

O Profit Pro (ou Profit Ultra) da Nelogica é a plataforma oficial de execução de ordens do CaM. ProfitDLL (ctypes) não é dependência da Fase 0–3 — avaliação somente quando houver necessidade real comprovada (Fase F4+).

A integração entre CaM backend e Profit cresce de forma faseada e sequencial:

| Fase de integração | O que acontece |
|---|---|
| F1 — Manual | CaM gera checklist/plano; Carlos opera manualmente no Profit; journal manual |
| F2 — CSV | CaM importa CSV/extrato Profit pós-pregão; concilia com journal |
| F3 — Semi-auto | CaM monitora estado do Profit em tempo real via export periódico |
| F4 — NTSL | Estratégia em NTSL com regras de risco espelhadas; CaM publica parâmetros |
| F5 — ProfitDLL | Avaliação futura — somente se necessidade real comprovar |

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | MetaTrader 5 (MT5) | Requer Linux (ou Wine no Windows); variante documentada mas não escolhida no MVP — complexidade adicional de SO sem benefício claro para WIN/WDO B3 |
| 2 | API direta da corretora | Não padronizado; varia por corretora; sem book visual para Carlos operar manualmente nas fases iniciais |
| 3 | ProfitDLL desde o início | Acoplamento imediato com DLL proprietária da Nelogica; risco de quebra sem aviso; overhead de manutenção para Fase 0 que não usa automação real |

---

## 4. Consequências

### Positivas
- Profit é o padrão do mercado BR para traders B3 — Carlos já conhece a interface
- NTSL é linguagem específica para automação no Profit — curva de aprendizado controlada
- Faseamento reduz risco: Carlos opera manualmente nas primeiras fases; automação vem depois
- Sem necessidade de API de corretora (fricção regulatória menor)

### Negativas
- Windows-only em produção — obrigatório manter stack bi-SO (Linux dev, Windows prod)
- Dependência de fornecedor único (Nelogica) — mudança de contrato ou preço impacta o projeto
- NTSL é linguagem proprietária — não há portabilidade para outro broker sem reescrever estratégias
- Módulo de Automação de Estratégias tem custo adicional (necessário para Fase F4)

### Neutras
- ProfitDLL (ctypes) fica como opção futura sem comprometimento de Fase 0
- A variante Linux+MT5 continua documentada como fallback não-ativo

---

## 5. Custo de Reversão

**Alto** — mudar de Profit para MT5 ou API direta de corretora exigiria reescrita das estratégias NTSL, mudança de SO de produção e revisão dos adapters de integração. Decisão cara de reverter após Fase F4.

---

## 6. Referências

- DAS: [`../DAS.md`](../DAS.md)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §6.1
- ADRs relacionadas: ADR-008 (faseamento), ADR-009 (NTSL como 2ª defesa), ADR-012 (dev/prod SO)
