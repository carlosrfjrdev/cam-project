---
template: SCOPE-EVOLUTION2
phase: DISC
status: Superseded — consolidado em SCOPE-Inspetor-Consolidado.md (2026-05-31)
version: 1.0
date: 2026-05-31
orchestrator: Leo
companion_of: SCOPE-Vision-Evolution.md
superseded_by: SCOPE-Inspetor-Consolidado.md
---

> ⚠️ **SUPERSEDED (2026-05-31):** este escopo foi consolidado em
> [`SCOPE-Inspetor-Consolidado.md`](./SCOPE-Inspetor-Consolidado.md). A abordagem de conexão MT5
> via `MetaTrader5` (Python lib) aqui descrita foi **substituída** por EA `cam_bridge` + ZeroMQ
> (estado real do código). A tabela de ocultação das 17 telas foi preservada no consolidado.
> Mantido apenas como histórico.

# SCOPE-Evolution2 — MVP Asset Research + Simplificação do Cockpit

> **Objetivo:** entregar uma tela de consulta de ativo funcional (busca → gráfico MT5 + fundamentalistas)
> e ocultar as 15 telas que ainda não fazem sentido no estado atual da Fase 0.
> Zero código deletado. Zero complexidade operacional exposta antes da hora.

---

## 1. Contexto e motivação

O cockpit atual tem 17 telas construídas e nenhuma delas é navegável de forma útil no estado presente
da Fase 0 (construção, sem trade real, sem paper trading ativo). O resultado prático é que Carlos
abre o cockpit e enfrenta um menu que promete mais do que o sistema entrega hoje.

A demanda do Founder é clara: **quero consultar um ativo — digito o símbolo, vejo o gráfico, vejo os
fundamentos.** Isso é MVP. O restante do cockpit existe e vai existir, mas não precisa estar visível
agora.

A estratégia é dupla:

1. **Simplificação imediata:** ocultar telas não-MVP no sidebar sem remover código — sidebar passa a
   refletir o que está pronto e é útil hoje.
2. **Construção do MVP:** tela `AssetResearchPage` com busca de símbolo, gráfico de candles via MT5 e
   painel de fundamentalistas (7 indicadores R-20 + dividendos recentes).

Este SCOPE é independente da `SPEC-v0.4-VISION-EVOLUTION.MD`. Não concorre com os blocos BL-A a BL-I
já planejados — é uma entrega paralela, menor, focada em navegabilidade e utilidade imediata.

---

## 2. Estratégia de simplificação (Ocultar + Revelar)

### 2.1 Classificação das 17 telas

| Tela | Path atual | Grupo nav atual | Decisao MVP |
|---|---|---|---|
| CockpitPage | `/` | Operação | VISIVEL-MVP — dashboard raiz |
| AssetResearchPage (nova) | `/asset-research` | Pesquisa | VISIVEL-MVP — tela principal desta demanda |
| ConstitutionPage | `/constitution` | Sistema | VISIVEL-MVP — referência constitucional sempre disponível |
| SettingsPage | `/settings` | Sistema | VISIVEL-MVP — configurações básicas |
| JournalPage | `/journal` | Registro | OCULTAR-AGORA — sem trade ativo |
| FiscalPage | `/fiscal` | Registro | OCULTAR-AGORA — sem trade ativo, sem DARF |
| HarvestPage | `/harvest` | Registro | OCULTAR-AGORA — sem aporte em andamento |
| BacktestPage | `/backtest` | Patrimônio | OCULTAR-AGORA — engine não tem dados reais ainda |
| PaperTradingPage | `/paper-trading` | Patrimônio | OCULTAR-AGORA — sem loop governado ativo |
| CarteiraHardPage | `/carteira-hard` | Patrimônio | OCULTAR-AGORA — sem holdings registradas |
| ResearchPage | `/research` | Patrimônio | OCULTAR-AGORA — substituída pelo MVP desta demanda |
| EaControlPage | `/ea-control` | Operação | OCULTAR-AGORA — sem EA ativo em papel |
| MarketDataPage | `/market-data` | Estratégia | OCULTAR-AGORA — substituída pelo MVP |
| OrderGatewayPage | `/order-gateway` | Operação | OCULTAR-AGORA — sem trade ativo |
| RiskConsolePage | `/risk` | Operação | OCULTAR-AGORA — Risk Engine não tem dados para exibir |
| RobotOrchestratorPage | `/robots` | Estratégia | OCULTAR-AGORA — sem robô ativo |
| ScalingPage | `/scaling` | Estratégia | OCULTAR-AGORA — pré-requisito BL-H não entregue |
| StrategyRegistryPage | `/strategies` | Estratégia | OCULTAR-AGORA — sem estratégia registrada |

**Resultado MVP:** 4 telas visíveis no sidebar (Cockpit, Asset Research, Constituição, Configurações).

### 2.2 Mecanismo de ocultamento

Implementação via array de rotas visíveis no arquivo `_shared/nav.tsx`. Cada item de `NAV_ITEMS`
ganha um campo opcional `visibleInMvp: boolean`. O `Sidebar.tsx` filtra pelo campo.

Alternativa equivalente: constante `MVP_VISIBLE_PATHS` em `nav.tsx` — sidebar exibe apenas os paths
presentes na lista. Rotas continuam registradas no `router.tsx` (navegação direta por URL funciona),
apenas desaparecem do menu.

Princípio inegociável: **sem deletar componente, rota ou teste**. Ocultar = remover do menu. Revelar
= adicionar de volta na lista.

---

## 3. MVP — Asset Research Screen

### 3.1 Visão da tela

```
+----------------------------------------------------------+
|  [Search: PETR4, WINM25, MXRF11...]   [Buscar]          |
+----------------------------------------------------------+
|  Símbolo: PETR4   Nome: Petróleo Brasileiro S.A.         |
|  Tipo: Ação   Exchange: B3   Moeda: BRL                  |
+----------------------------------------------------------+
|  Timeframe: [M1][M5][M15][M30][H1][H4][D1][W1][MN1]     |
|                                                          |
|  +----------------------------------------------------+  |
|  |                                                    |  |
|  |         Gráfico de Candles                         |  |
|  |         (TradingView Lightweight Charts)           |  |
|  |                                                    |  |
|  +----------------------------------------------------+  |
+----------------------------------------------------------+
|  TICKS RECENTES (últimos 20)                             |
|  Time         Bid      Ask      Last     Volume  Flags   |
|  14:32:01.234 28.15    28.16    28.15    100     ...     |
|  ...                                                     |
+----------------------------------------------------------+
|  BOOK / DOM  [somente se disponível no símbolo]          |
|  Compra   Preço   Venda                                  |
|  500       28.15   300                                   |
|  ...                                                     |
+----------------------------------------------------------+
|  FUNDAMENTALISTAS  [somente para Ações e FIIs]           |
|  +----------+ +----------+ +----------+ +----------+    |
|  | DY       | | P/L      | | P/VP     | | ROE      |    |
|  | 8.4%     | | 12.3x    | | 1.2x     | | 18.5%    |    |
|  +----------+ +----------+ +----------+ +----------+    |
|  +----------+ +----------+ +----------+                 |
|  | Div/EBITDA| | Payout  | | ROIC     |                 |
|  | 1.8x      | | 65%     | | 14.2%    |                 |
|  +----------+ +----------+ +----------+                 |
|                                                          |
|  DIVIDENDOS RECENTES                                     |
|  Data        Tipo     Valor    Yield    Status           |
|  2025-03-15  DY       R$1.20   2.1%    Pago             |
|  ...                                                     |
+----------------------------------------------------------+
```

### 3.2 Componentes da tela

**Busca de símbolo**
- Campo de texto com autocomplete
- Fonte do autocomplete: `/api/v1/market/symbols` (lista de símbolos disponíveis no MT5 conectado)
- Universo: ações B3 (`PETR4`, `VALE3`), FIIs (`MXRF11`), derivativos (`WIN$`, `WINM25`, `WDO$`)
- Símbolo selecionado alimenta todos os demais componentes da tela

**Seletor de timeframe**
- Botões: M1 M5 M15 M30 H1 H4 D1 W1 MN1
- Mapeia para constantes `TIMEFRAME_*` da Python lib MetaTrader5
- Padrão inicial: H1

**Gráfico de candles**
- Lib: `lightweight-charts` (TradingView)
- Dados: `/api/v1/market/data/{symbol}?timeframe=H1&limit=200`
- Estrutura retornada: array de `{ time, open, high, low, close, volume }`
- Origem dos dados: `copy_rates_from()` via MT5Service no backend
- Sem streaming no MVP — refresh manual ou por intervalo configurável (ex.: 30s)

**Painel de ticks**
- Tabela dos últimos N ticks (padrão 20, configurável)
- Rota: `/api/v1/market/data/{symbol}/ticks?limit=20`
- Colunas: `time`, `bid`, `ask`, `last`, `volume`, `flags`
- Origem: `copy_ticks_from()` via MT5Service
- Atualização via WebSocket (BL-4) ou polling no MVP inicial

**Book / DOM**
- Exibido condicionalmente — só quando `market_book_add()` retornar dados válidos
- Tabela bid/ask com volumes por nível de preço
- Rota: `/api/v1/market/data/{symbol}/book`
- Se não disponível: mensagem discreta "Book não disponível para este símbolo"

**Seção de fundamentalistas**
- Exibida condicionalmente — apenas para tipo `Ação` e `FII`
- Para `Derivativo`: seção oculta sem mensagem de erro (comportamento esperado)
- Cards dos 7 indicadores R-20 (ver seção 6)
- Fonte primária: brapi.dev; fallback: Fundamentus scraping
- Rota: `/api/v1/fundamentals/{symbol}`

**Tabela de dividendos recentes**
- Colunas: `data_pagamento`, `tipo` (DY/JCP), `valor_por_cota`, `yield_na_data`, `status`
- Últimos 12 eventos ou 2 anos, o que vier primeiro
- Fonte: brapi.dev dividends endpoint; fallback: Fundamentus
- Rota inclusa na mesma resposta de `/api/v1/fundamentals/{symbol}`

---

## 4. Features IN / OUT / LATER

### IN (MVP — este escopo)

- Ocultamento de 13 telas no sidebar (sem deletar código)
- Rota e componente `AssetResearchPage`
- Autocomplete de símbolos via MT5
- Busca de candles (histórico, sem stream) com gráfico Lightweight Charts
- Seletor de timeframe (M1 a MN1)
- Tabela de ticks recentes (polling ou snapshot)
- Book/DOM condicional (exibido se disponível, oculto se não)
- Seção de fundamentalistas condicional (ações e FIIs apenas)
- 7 indicadores R-20: DY, P/L, P/VP, ROE, Dívida Líq/EBITDA, Payout, ROIC
- Tabela de dividendos recentes
- Fontes: brapi.dev (primário) + Fundamentus scraping (fallback)

### OUT (este MVP)

- Streaming de candles em tempo real via WebSocket (polling é suficiente no MVP)
- Alertas de preço ou notificações
- Comparação de múltiplos símbolos na mesma tela
- Annotations no gráfico (suporte, resistência, linhas manuais)
- Exportação de dados (CSV, PDF)
- Cache persistente de dados fundamentais (cache em memória é aceitável no MVP)
- Integração com Risk Engine nesta tela
- Qualquer envio de ordem — tela é puramente read-only (Art. 35)

### LATER (próximos blocos — a partir do SCOPE-Vision-Evolution BL-F e BL-G)

- Streaming real de candles e ticks via WebSocket persistente
- Reexibição das telas ocultadas à medida que seus pré-requisitos forem cumpridos
- Cross-Asset Pattern Lab (correlação ação/derivativo)
- AI Research Workbench integrado à tela
- Rebalance Suggestion para Carteira Hard
- Pair Trade Research
- Instrument Catalog amplo (200+ ativos com metadados enriquecidos)

---

## 5. Dependências técnicas

### 5.1 Backend — serviços novos

**MT5Service** (`cam/features/market_data/mt5_service.py`)
- Wrapper sobre a lib Python `MetaTrader5`
- Métodos principais:
  - `get_symbols() -> list[str]` — lista de símbolos disponíveis
  - `get_rates(symbol, timeframe, limit) -> list[OHLCV]` — via `copy_rates_from()`
  - `get_ticks(symbol, limit) -> list[Tick]` — via `copy_ticks_from()`
  - `get_book(symbol) -> BookSnapshot | None` — via `market_book_add()` + `market_book_get()`
- Requisito: MT5 instalado e logado no Windows 11 (já confirmado pelo Founder)
- Conexão lazy com reconexão automática

**FundamentalsService** (`cam/features/fundamentals/service.py`)
- Fonte primária: brapi.dev REST API (endpoint `/quote/{ticker}` + `/quote/{ticker}?dividends=true`)
- Fonte fallback: Fundamentus scraping (HTML parsing seguro, sem bypass de login)
- Rate limiting respeito às políticas das fontes
- Cache em memória com TTL (ex.: 1h para fundamentais, 5min para dividendos)
- Retorno tipado com os 7 indicadores R-20 + lista de dividendos

**Rotas novas** (`cam/api/v1/market/` e `cam/api/v1/fundamentals/`)

| Rota | Método | Descrição |
|---|---|---|
| `/api/v1/market/symbols` | GET | Lista símbolos disponíveis no MT5 |
| `/api/v1/market/data/{symbol}` | GET | Candles OHLCV (params: timeframe, limit) |
| `/api/v1/market/data/{symbol}/ticks` | GET | Ticks recentes (param: limit) |
| `/api/v1/market/data/{symbol}/book` | GET | Book/DOM snapshot (null se indisponível) |
| `/api/v1/fundamentals/{symbol}` | GET | 7 indicadores R-20 + dividendos |

### 5.2 Frontend — libs novas e componentes

**Dependência nova**
- `lightweight-charts` (TradingView) — instalar via npm/yarn

**Componentes novos** (`src/features/asset-research/`)
- `AssetResearchPage.tsx` — container da tela
- `SymbolSearch.tsx` — campo de busca com autocomplete
- `TimeframeSelector.tsx` — botões M1 a MN1
- `CandleChart.tsx` — wrapper do `lightweight-charts`
- `TicksTable.tsx` — tabela de ticks recentes
- `BookTable.tsx` — book/DOM condicional
- `FundamentalsPanel.tsx` — container condicional (ação/FII only)
- `IndicatorCard.tsx` — card individual de indicador R-20
- `DividendsTable.tsx` — tabela de dividendos recentes

**Alterações em arquivos existentes**
- `_shared/nav.tsx` — adicionar campo `visibleInMvp` + rota da nova tela
- `_shared/components/Sidebar.tsx` — filtrar itens por `visibleInMvp`
- `app/router.tsx` — adicionar rota `/asset-research`

---

## 6. Indicadores R-20 por tipo de ativo

| Indicador | Acao | FII | Derivativo |
|---|---|---|---|
| DY (Dividend Yield) | Sim | Sim | Nao |
| P/L (Preco / Lucro) | Sim | Nao (FII usa P/FFO) | Nao |
| P/VP (Preco / Valor Patrimonial) | Sim | Sim | Nao |
| ROE (Return on Equity) | Sim | Nao | Nao |
| Divida Liq / EBITDA | Sim | Nao (FII nao tem EBITDA) | Nao |
| Payout | Sim | Sim | Nao |
| ROIC (Return on Invested Capital) | Sim | Nao | Nao |

**Nota sobre FIIs:** brapi.dev retorna `dividendYield`, `pvp` e `dividends` para FIIs. Os campos
ausentes (P/L, ROE, Divida/EBITDA, ROIC) ficam com exibicao `N/A` + tooltip explicativo
("Indicador nao aplicavel para FIIs").

**Nota sobre derivativos:** secao de fundamentalistas completamente ocultada para `WIN$`, `WINM25`,
`WDO$` e similares. Nao exibir mensagem de erro — ausencia e o comportamento correto.

---

## 7. Sequencia de execucao (blocos)

A execucao segue ordem de dependencia. Cada bloco e um entregavel independente que o Founder
aprova antes do proximo iniciar (gate proporcional a tamanho do bloco).

| Bloco | Entregavel | Tamanho | Pré-requisito |
|---|---|---|---|
| **BL-1** | Ocultamento das 13 telas no sidebar + rota `/asset-research` vazia | P | Nenhum |
| **BL-2** | MT5Service (symbols + rates + ticks + book) + rotas backend | M | MT5 logado no Windows |
| **BL-3** | Frontend: SymbolSearch + TimeframeSelector + CandleChart (dados históricos) | M | BL-2 |
| **BL-4** | Ticks em tempo real (WebSocket ou polling com atualização automática) | M | BL-2 |
| **BL-5** | Book/DOM condicional na tela | P | BL-2 |
| **BL-6** | FundamentalsService (brapi.dev + Fundamentus fallback) + rota backend | M | Nenhum (paralelo a BL-2) |
| **BL-7** | Frontend: FundamentalsPanel + IndicatorCard + DividendsTable | M | BL-3 + BL-6 |

BL-1 e BL-6 podem rodar em paralelo com BL-2. BL-7 depende de BL-3 e BL-6 entregues.

---

## 8. Riscos e mitigacoes

| Risco | Probabilidade | Impacto | Mitigacao |
|---|---|---|---|
| MT5 nao conectado no momento do request | Media | Medio | MT5Service retorna erro descritivo; frontend exibe banner "MT5 desconectado — abra o terminal" |
| Book/DOM indisponivel para o simbolo | Alta (maioria dos ativos) | Baixo | Comportamento por design: secao Book oculta se `market_book_add()` retornar False |
| brapi.dev rate limit atingido | Media | Medio | Cache com TTL + fallback para Fundamentus automatico; indicadores exibidos como "Atualizando..." |
| Fundamentus scraping quebra (mudanca de HTML) | Media | Medio | Erro isolado no fallback nao derruba a tela; indicadores ficam como "Indisponivel" |
| Simbolo sem dado fundamental (ex.: ativo novo) | Baixa | Baixo | FundamentalsService retorna objeto parcial; frontend exibe N/A por campo ausente |
| lightweight-charts incompatibilidade com React 19 | Baixa | Alto | Verificar versao compativel antes de instalar; alternativa: recharts como fallback |
| Tela em conta real — leitura inadvertida de dados sensiveis | Baixa | Alto | MT5Service e estritamente read-only (copy_rates, copy_ticks, market_book_get); nenhuma ordem, nenhum envio de comando ao terminal (Art. 35) |

**Nota constitucional:** esta tela opera em modo puramente read-only. Nenhum componente envia ordem,
parametriza Risk Engine ou justifica excecao constitucional. Art. 35 e respeitado por design de
escopo — nao por restricao de codigo.

---

## 9. Proxima acao

Para avancar para ARCH + SPEC, o Founder precisa aprovar os seguintes pontos:

1. **Classificacao das telas** — a lista IN/OUT do sidebar (secao 2.1) esta correta? Alguma tela
   marcada como OCULTAR-AGORA deveria permanecer visivel?

2. **Universo de simbolos** — o autocomplete parte dos simbolos disponiveis no MT5 conectado
   (dinamico) ou de uma lista curada manualmente (estatica + MT5)?

3. **Modo de atualizacao de candles** — polling com intervalo fixo e suficiente para MVP, ou
   WebSocket de candles e prioridade ja no BL-3?

4. **Ticks em tempo real (BL-4)** — WebSocket ja no MVP ou tabela de snapshot (refresh manual) e
   aceitavel inicialmente?

5. **AssetResearchPage substitui MarketDataPage e ResearchPage** — ou ambas permanecem como telas
   distintas (ocultas agora, reativadas depois com funcoes diferentes)?

Aprovados esses pontos, Leo invoca Oscar (ARCH) para DAS + ADRs e Albert (SPEC) para especificacao
detalhada dos 7 blocos.

---

## Referencias cruzadas

- `SCOPE-Vision-Evolution.md` — backlog estruturado maior; esta demanda e paralela, nao conflita
- `project/STACK-CAM-OFICIAL.md` — stack oficial (Python/FastAPI, React 19/Vite/MUI, Windows 11)
- `CONSTITUICAO.md` Arts. 35 e 36 — tela read-only por design constitucional
- `apps/cam-cockpit/frontend/src/_shared/nav.tsx` — arquivo a modificar no BL-1
- `apps/cam-cockpit/frontend/src/app/router.tsx` — arquivo a modificar no BL-1
- Feature `market-data` existente: `apps/cam-cockpit/frontend/src/features/market-data/` — referencia para reaproveitamento
- Feature `research` existente: `apps/cam-cockpit/frontend/src/features/research/` — referencia para reaproveitamento
