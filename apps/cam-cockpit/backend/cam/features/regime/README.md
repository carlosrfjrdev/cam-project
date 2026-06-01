# regime — Overlay de Regime de Markov (read-only)

> **Status:** ATIVA (ADR-014 / SPEC-Inspetor BL-8)
> **Papel constitucional:** "assistente de pesquisa" (Arts. 13/34–36, ADR-006)

## Propósito

Classifica o regime de mercado (Bull/Sideways/Bear) de uma **ação** a partir da
série de close diária, expõe matriz de transição, distribuição estacionária,
sinal e métricas de backtest walk-forward. **Read-only — papel A.** Nunca emite
ordem nem dimensiona posição (papéis B/C ficam fora — Parte VII).

## I/O

- `GET /api/v1/regime/{symbol}?timeframe=D1&window=20&threshold=0.05`
- Lê `cam_inspector_candles` (populada por `/mt5/candles?timeframe=D1`).

## Acoplamento (ADR-013)

Slice auto-contido. **Não importa** `mt5_integration` nem `fundamentals`. O único
ponto de contato é a tabela de banco `cam_inspector_candles`.

## Atribuição (R-23)

Matemática vendorizada do framework de Roan (@RohOnChain), refatorado por
Lewis Jackson. **Sem** o caminho yfinance. **Proibido** rodar o instalador
`markov-hedge-fund-method.md` (R-24).

## Caveats honestos (R-26 — expostos, não escondidos)

- Rótulo é tendência **defasada**; janelas sobrepostas autocorrelacionam → a
  persistência da matriz é em parte artefato.
- Backtest usa `sign(sinal)` e **não** modela custo/spread → Sharpe é **bruto**.
- Regime diário é filtro macro grosseiro; para a S1 (ORB 60m WIN) é contexto.

## Anti-padrões

- ❌ Emitir sinal de execução / dimensionar posição (papéis B/C).
- ❌ Importar outra feature (ADR-013).
- ❌ Reintroduzir o caminho yfinance ou o instalador (SEC-GOV/Kevin).
