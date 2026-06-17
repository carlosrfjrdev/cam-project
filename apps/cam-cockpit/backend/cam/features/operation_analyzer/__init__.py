"""
operation_analyzer — Analisador de Operação (CASCA / SHELL — Fase 0).

Cenário: o usuário entra com ticks + candles + estratégia → o CAM SINALIZA as
operações e mostra em tela: risco analisado, melhor horário e mão (tamanho).
Regra de alvo: sempre R:R 1:3.

⚠️ SHELL: a engine de sinais ainda NÃO está implementada — os endpoints retornam
um contrato estável com dados STUB para a UI ser construída em cima. SEM bloqueios
de Risk Manager por design (é sinalização/análise, não trava operacional).
"""
