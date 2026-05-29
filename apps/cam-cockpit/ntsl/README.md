# ntsl/ — DESATIVADO em 2026-05-25

> Esta pasta está **DESATIVADA** após adoção de MT5 + MQL5 conforme
> [SPEC v0.2.1](../../../project/cam-cockpit/SPEC-v0.2-MT5-ENQUADRAMENTO.md)
> e [DECISION-MEMO](../../../project/DECISION-MEMO-LINUX-OR-WINDOWS.md) §6.

## Status

| Campo | Valor |
|---|---|
| Estado | **DESATIVADO** |
| Desde | 2026-05-25 |
| Decisão | DECISION-MEMO §6 — Opção B (Linux + MT5 + MQL5) |
| Princípio | Coexistência (SPEC v0.2.1 §R21) — código NÃO removido |
| Stack ativa de execução | [`apps/cam-cockpit/mql5/`](../mql5/) |

## Por que permanece no repositório

Princípio de Coexistência (SPEC v0.2.1 R21.01): novas camadas são adicionadas
em paralelo, código antigo não é arquivado prematuramente. Isso garante
**reversibilidade barata** caso o caminho MT5 falhe em paper trading e seja
necessário voltar para NTSL/Profit.

## Como reativar (futuro)

Reativação exige:

1. Decisão formal registrada (similar a emenda — ver [`PROTOCOLO-EMENDA-CONSTITUCIONAL.md`](../../../project/PROTOCOLO-EMENDA-CONSTITUCIONAL.md)).
2. Editar `.env` do backend:
   ```bash
   PROFIT_INTEGRATION_ENABLED=true
   MT5_INTEGRATION_ENABLED=false
   ```
3. Restart do backend — o mutex R21.03 valida que apenas uma camada está ativa.
4. Remover este banner deste README.

## Estrutura (preservada)

Como esta pasta foi apenas scaffold da SPEC v0.1 (T-A01), está vazia.
Quando havia código real, ele permaneceria intocado aqui.
