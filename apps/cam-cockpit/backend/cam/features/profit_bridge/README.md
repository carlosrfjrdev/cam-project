# profit_bridge — Bridge de ticks READ-ONLY do Profit (ProfitDLL)

> **Status:** SCAFFOLD (2026-06-17). Código pronto; falta ligar com credenciais reais.
> Análogo ao [`mt5_integration`](../mt5_integration/), porém via **ProfitDLL** (DLL
> oficial Nelogica, in-process/ctypes) em vez de ZeroMQ.

## Propósito

Ler **negócios/ticks** do Profit (preço, qtd, volume e **agressor** comprador/vendedor)
e publicar em `cam_market_ticks` com `source="profit.profitdll"`. Lane de **market-data
read-only** — login `DLLInitializeMarketLogin` (sem roteamento). **Nenhuma função de
ordem é declarada** (read-only por construção); fica fora do mutex de execução R21.03.

## Componentes

| Arquivo | Papel |
|---|---|
| `types.py` | Structs ctypes do subconjunto read-only (TConnectorTrade, callbacks) |
| `client.py` | `ProfitBridgeClient`: load DLL, login market-only, callbacks → tick normalizado, subscribe, histórico |
| `persister.py` | `ProfitTickPersister`: buffer thread-safe + flush em lote → `cam_market_ticks` |
| `runner.py` | Entrypoint standalone (Windows): ao vivo ou histórico do dia |

## Pré-requisitos

1. **Windows** + **ProfitChart** logado (ou a DLL faz o login com as credenciais).
2. **ProfitDLL liberado na conta** + **chave de ativação** (Nelogica).
3. SDK na máquina — a DLL fica em `ProfitDLL/DLLs/Win64/ProfitDLL.dll` (não commitado).

## Configuração (`.env`)

```dotenv
PROFIT_DLL_ENABLED=true
PROFIT_DLL_PATH=D:/DEV/Teczilabs/cam-project/ProfitDLL/DLLs/Win64/ProfitDLL.dll
PROFIT_DLL_KEY=<chave de ativacao Nelogica>
PROFIT_USERNAME=<email/documento da conta>
PROFIT_PASSWORD=<senha da conta>
PROFIT_DEFAULT_EXCHANGE=F   # B3 derivativos (WIN/WDO)
```

## Uso

```bash
cd apps/cam-cockpit/backend
# ao vivo (grava tick a tick em cam_market_ticks):
uv run python -m cam.features.profit_bridge.runner --ticker WINFUT
# histórico de um dia e sai:
uv run python -m cam.features.profit_bridge.runner --ticker WINFUT --history 2026-06-17
```

O `--ticker` aceita o contínuo (`WINFUT`) ou o vencimento (`WINM26`); a bolsa default
é `F`. Os ticks entram no mesmo corpus do MT5 → os analyzers ganham o Profit como
**segunda fonte** (comparável ao MT5 na mesma janela).

## Estado de conexão (callback de estado)

`is_ready()` = `connected` (login) **e** `market_connected` (market) **e** `activated`
(licença/chave OK). Se não ficar pronto: chave inválida, conta sem ProfitDLL liberado,
ou sem market-data — ver códigos `NL_*` no Manual ProfitDLL.

## Anti-padrões

- ❌ Declarar/charmar qualquer função de ordem (SendOrder, ZeroPosition...) — read-only.
- ❌ Commitar a DLL, os PDFs do SDK ou segredos do `.env`.
- ❌ Bloquear o callback da DLL (só enfileira; o flush é assíncrono).

## Próximo passo de integração

Apontar o auto-fetch de ticks dos analyzers para `cam_market_ticks` (fonte `profit*`
ou `mt5*`) quando a bridge MT5 estiver offline — hoje o auto-fetch chama só o MT5.
