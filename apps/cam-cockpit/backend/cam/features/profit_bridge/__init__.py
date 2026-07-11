"""
profit_bridge — Bridge de ticks READ-ONLY do Profit (Nelogica) via ProfitDLL.

Análogo ao `mt5_integration` (cam_bridge), porém o transporte é a **ProfitDLL**
(DLL oficial, in-process via ctypes) em vez de ZeroMQ. Login **market-data only**
(`DLLInitializeMarketLogin`) — NÃO há roteamento de ordem aqui por design (read-only,
fora do mutex de execução R21.03).

Fluxo: DLL → callbacks de negócio (preço/qtd/volume/**agressor**) → normaliza →
publica em `cam_market_ticks` com `source="profit.profitdll"`. Os analyzers e o
corpus passam a ter o Profit como segunda fonte (comparável ao MT5).

⚠️ Windows-only. Requer ProfitDLL liberado na conta + chave de ativação (.env).
"""
