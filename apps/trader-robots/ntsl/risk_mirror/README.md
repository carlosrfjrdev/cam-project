# NTSL Risk Mirror

Segunda linha de defesa constitucional — regras do Risk Engine espelhadas em NTSL (Nelogica Trading System Language) dentro do Profit.

## Propósito (ADR-009)

O Risk Engine Python é a fonte de verdade. O NTSL Risk Mirror é uma segunda camada de proteção rodando DENTRO do Profit, independente do cockpit. Se o backend Python falhar, o Profit ainda rejeita ordens que violem os limites constitucionais.

## Status

Fase 0 — Construção. Esta pasta existe como estrutura. O conteúdo NTSL será implementado a partir da Fase 1 (paper trading ativo).

## Regras a Espelhar (prioridade constitucional)

1. Limite absoluto: 2 contratos WIN / 2 contratos WDO (Art. 11)
2. Kill switch ativo = sem ordens (Art. 18)
3. Limite de perda diária 3% (Art. 16)
4. Martingale proibido (Art. 13)

## Paridade

Testes de paridade NTSL x Python por cenário canônico serão criados antes de qualquer integração F3+.
