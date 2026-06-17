"""
trade_analyzer — Analisador de Trades do CaM.

Sobe o report de operações (CSV Profit/Genial) + ticks opcionais → calcula
métricas determinísticas no código (confiáveis) e envia um resumo para uma IA
(Claude ou OpenAI, escolhida na UI) para análise qualitativa de erros e correções.

Sem bloqueios de Risk Manager — é diagnóstico, não trava operacional.
"""
