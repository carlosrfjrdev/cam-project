---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-014 — MT5 como fonte de market data read-only (via EA `cam_bridge` + ZeroMQ)

> **Data:** 2026-05-31
> **Status:** Aceita — aprovada pelo Founder
> **Lead:** Oscar · **Cross-cutting:** Kevin (SEC-GOV)
> **Aprovador final:** Carlos Rodrigues Ferreira Junior (Founder)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-014-mt5-market-data-read-only.md`

---

## 1. Contexto

A SPEC `SPEC-Inspetor-de-Ativo.md` (aprovada 2026-05-31) entrega o primeiro slice vertical de
**dado de mercado ao vivo** do CaM — o Inspetor de Ativo. Para isso precisa de uma fonte oficial de
candles, tick e book.

O DAS (2026-05-24) está **desatualizado** quanto a este ponto:

- §2 e §9 ainda tratam **Profit/Nelogica** como plataforma e listam **"MT5 como fallback —
  out-of-scope"**.
- ADR-016/008/012 ainda dizem **Profit** + **dev-Linux/prod-Windows**.

A recalibração registrada em 2026-05-30 (commits `79a0680`, `5f884d9`, `73d4bde`) tornou
**Windows 11 o SO firme** (Wine/Linux falhou) e colocou **MT5 em teste como broker** (Profit em
standby). O estado real do código confirma a direção: o EA `cam_bridge.mq5` (v0.3) **já existe**,
é **read-only por construção** e publica tick/heartbeat/posição via **ZeroMQ** — não há nenhum
caminho `MetaTrader5` (Python lib) no código operacional.

Esta ADR formaliza a fonte de **dados** (não de execução), destravando o Inspetor sem antecipar a
decisão de broker de execução (OP-014/OP-015, ainda aberta).

## 2. Decisão

**O MT5 é a fonte oficial de market data do CaM, consumida exclusivamente em modo read-only através
do EA `cam_bridge` sobre ZeroMQ (loopback 127.0.0.1).**

1. **Canal único:** EA `cam_bridge.mq5` → ZeroMQ → backend `features/market_data/`. O pacote Python
   `MetaTrader5` **não** entra no caminho operacional.
2. **Read-only por construção:** o EA não contém — e não pode conter — `OrderSend`/`OrderClose`/
   `PositionOpen`/`PositionClose` (CA15.1). O canal REP é **allowlistado** (CA15.3); comandos novos
   desta decisão (`GET_CANDLES`, `GET_SYMBOLS`, `SUBSCRIBE`, `UNSUBSCRIBE`) são **todos de leitura**.
   Comandos de escrita vivem apenas em `cam_risk_mirror.mq5`, fora deste perímetro.
3. **Escopo é dado, não execução:** esta ADR **não** decide o broker de execução. ADR-016 (Profit)
   permanece formalmente vigente até OP-014/OP-015 fecharem; a decisão de *dados* é independente da
   de *ordens*.
4. **Conta REAL permitida em read-only:** como o bridge é estruturalmente read-only, consumir dados
   de uma conta MT5 **real** é seguro. O guard `InpRequireDemoAccount` do EA pode ser setado
   `false` **conscientemente**, condicionado aos controles SEC-GOV da §4 (banner REAL, allowlist
   sem escrita, audit log).
5. **Persistência com proveniência:** todo tick recebido é gravado em `cam_market_ticks`
   (`source="mt5.cam_bridge"`); continuous aggregates geram `cam_candles_*`.

## 3. Alternativas consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | Pacote Python `MetaTrader5` (poll direto do terminal) | Windows-only; poll-based (sem streaming real de tick/book via `OnBookEvent`); **diverge do código já existente** (EA+ZeroMQ); não oferece a propriedade "read-only por construção" do EA. Estado real vence intenção (NCC-1701 §2). |
| 2 | Manter Profit/Nelogica como fonte de dados (DAS atual) | Profit está em **standby** (recalibração 2026-05-30); nenhum código de integração Profit ativo; bloquearia o Inspetor por uma decisão de broker ainda aberta. |
| 3 | Esperar OP-014/OP-015 (decisão de broker) antes de definir a fonte de dados | Acopla desnecessariamente *dados* a *execução*; trava um slice read-only e seguro atrás de uma decisão de execução que não o afeta. |

## 4. Consequências

### Positivas
- Destrava o Inspetor (SPEC aprovada) sem antecipar a decisão de broker de execução.
- Aproveita o EA `cam_bridge` já construído e a stack ZeroMQ já documentada.
- Read-only por construção é uma garantia **estrutural** (não-flag) alinhada aos Arts. 13/34–36.
- Semeia o corpus de tick com proveniência limpa (um canal só) para a trilha preditiva futura.

### Negativas
- EA single-thread: `GET_CANDLES` grande pode segurar o heartbeat → mitigado por limite de `count`.
- Requer o terminal MT5 aberto e o EA atachado para haver dado ao vivo.
- Operar em conta REAL exige disciplina de configuração (`InpRequireDemoAccount=false` consciente).

### Neutras
- O DAS precisa ser corrigido na linha de market data (ver §6) — feito junto desta ADR.
- ADR-016/008/012 permanecem como estão até OP-014/OP-015; esta ADR não os revoga.

### Controles SEC-GOV (Kevin) — condição de aceite para conta REAL
1. Banner **REAL** permanente no header do cockpit enquanto a conta for real.
2. Verificação automatizada de que a allowlist do EA **não** contém comando de escrita
   (`grep OrderSend` no `.mq5` = vazio; teste de allowlist rejeitando comando fora da lista).
3. Audit log da sessão de market data (structlog).

## 5. Custo de reversão

**Baixo–médio.** Trocar a fonte de dados (ex.: voltar a Profit ou adotar feed pago) afeta apenas
`features/market_data/` e o EA — os contratos REST/WS para o frontend permanecem estáveis. Não é
decisão de fundação.

## 6. Referências

- SPEC: [`../specs/SPEC-Inspetor-de-Ativo.md`](../specs/SPEC-Inspetor-de-Ativo.md) (aprovada 2026-05-31)
- SCOPE: [`../scopes/SCOPE-Inspetor-Consolidado.md`](../scopes/SCOPE-Inspetor-Consolidado.md)
- DAS: [`../DAS.md`](../DAS.md) — §2 (camadas) e §9 (não-decisões) corrigidos por esta ADR
- Código: `apps/cam-cockpit/mql5/experts/cam_bridge.mq5` (v0.3), `mql5/include/cam_zmq.mqh`
- ADRs relacionadas: ADR-013 (vertical slice), ADR-006 (IA sem autoridade), ADR-004 (TimescaleDB);
  ADR-016/008/012 (Profit/dev-Linux) **não revogadas** — pendentes de OP-014/OP-015
- Decisões abertas: OP-014 (MT5 vs Profit execução), OP-015 (gate de broker)
