# Análise de viabilidade — Bridge de ticks do Profit (Nelogica) para análise

> Pergunta do Founder (2026-06-17): "tem como montar um bridge de ticks para
> análise direto do Profit?" (MT5 já online via `cam_bridge`).
> Escopo: **ingestão de ticks read-only para análise** (alimentar `cam_market_ticks`
> e os analyzers), NÃO roteamento de ordem.

## Veredito

**Sim, é viável — mas o transporte é o ProfitDLL, não o NTSL.** O caminho
arquiteturalmente correto é um cliente **ProfitDLL** (Python/ctypes) que assina os
callbacks de negócios/book e publica no mesmo corpus `cam_market_ticks` (campo
`source="profit.profitdll"`), espelhando o que o `cam_bridge` MQL5 faz hoje. Os
analyzers funcionam **sem mudança** (a ingestão é desacoplada por `source`).

## Por que NTSL NÃO serve de bridge

O NTSL é uma linguagem de **estratégia/indicador rodando dentro do ProfitChart**,
em sandbox. Confirmado no `manualNTSL.md`:
- **Lê** dado rico: `Trades`, `VolumeAgent` (agressor), `VolumeAtPrice`, funções de
  book (`BookSpread`, profundidade) — ou seja, microestrutura completa.
- **Não tem** I/O externo: sem socket, sem gravação de arquivo, sem chamada de DLL,
  sem HTTP/TCP. O único "exportar" do manual é *exportar a estratégia* (o `.src`),
  não dados em tempo real.
- Saída possível: apenas plot no gráfico e envio de ordem. **Não dá para empurrar
  tick para fora.** (≠ MQL5, que chama DLL/ZeroMQ — por isso o MT5 vira bridge.)

Conclusão: NTSL continua útil para **replicar estratégia** (validação tripla
Profit×MT×CAM), mas **não** como canal de dados.

## Opções de transporte do Profit → CAM

| Opção | Tempo real? | Esforço | Veredito |
|---|---|---|---|
| **ProfitDLL** (C/.NET DLL oficial, via ctypes) | ✅ sim (callbacks) | Médio | **Recomendado** — é o equivalente do bridge MT5 |
| **Export CSV (Times & Trades)** do ProfitChart | ❌ manual/batch | Zero | **Disponível hoje** para análise pós-pregão |
| RTD (Excel) / DDE (legado) | parcial/frágil | Médio | ❌ não recomendado |
| NTSL | — | — | ❌ não serve (sandbox) |

## Caminho recomendado — `profit_bridge` via ProfitDLL

Espelha a arquitetura do `mt5_integration`:

1. **Cliente ProfitDLL (Python/ctypes), Windows-only.** Login na DLL, `SubscribeTicker`
   do ativo (ex.: WINFUT/WIN), registra callbacks de **negócios** (preço, volume,
   **agressor** comprador/vendedor) e, se quiser, book. Histórico do dia via a função
   de histórico de negócios da DLL (`GetHistoryTrades`-equivalente) → cobre o
   "ticks do dia automático" igual ao `get_ticks_range` do MT5.
2. **Normaliza e publica** no contrato interno existente: insere em `cam_market_ticks`
   com `source="profit.profitdll"` (reusa o padrão do `TickPersister` — buffer + flush
   em lote, best-effort, não derruba o stream).
3. **Analyzers não mudam.** Trade/Operation Analyzer já leem por `source`/símbolo; só
   passam a ter uma segunda fonte. Dá até para **comparar** Profit×MT5 (mesma janela)
   — fortalece a validação tripla.

### Reuso direto do que já existe
- `cam_market_ticks` (corpus + schema) — pronto.
- `TickPersister` (padrão de buffer/flush) — replicável.
- `profit_integration/` (CSV importer + reconciliação) — já existe; o bridge é a
  camada **realtime** que faltava ao lado do CSV.
- Contrato de ingestão por `source` — os analyzers já abstraem a fonte.

## Riscos / pré-requisitos a confirmar (HARD antes de codar)

1. **Entitlement Nelogica:** ProfitDLL exige conta habilitada (Profit Pro/DMA) +
   **chave de ativação** da DLL. Confirmar com a Nelogica se a sua conta tem acesso
   ao ProfitDLL (não vem ligado por padrão).
2. **Market data B3:** dado em tempo real via DLL pode ter implicações de contrato de
   market data (igual ao terminal). Verificar termos.
3. **API surface por versão:** nomes/assinaturas dos callbacks variam por versão do
   ProfitDLL — fixar contra o manual da DLL **da versão instalada** (não assumir).
4. **Mutex R21.03 (execução):** hoje só UMA camada de **integração de broker** fica
   ativa (Profit *ou* MT5). Esse mutex é sobre **ordem**. Para um bridge **read-only
   de market data**, separar a *lane* de ingestão do mutex de execução (decisão de
   arquitetura — vira ADR). Assim Profit-ticks e MT5-ticks coexistem para análise.
5. **Windows-only + single-thread de callback:** buffering cuidadoso (como o
   TickPersister) para não travar o callback da DLL.

## Próximos passos sugeridos

- **Agora (zero código):** exportar o **Times & Trades** do dia no ProfitChart para
  CSV e subir no analyzer — valida o valor da microestrutura do Profit imediatamente.
- **Se for evoluir:** abrir ADR (`teczi-architecture-decision`) decidindo (a) separar a
  lane de market-data do mutex de execução e (b) adotar ProfitDLL; depois SPEC+PLAN
  do `profit_bridge` reusando o padrão do `mt5_integration`.
- **Bloqueante externo:** confirmar com a Nelogica o acesso ao ProfitDLL + chave.
