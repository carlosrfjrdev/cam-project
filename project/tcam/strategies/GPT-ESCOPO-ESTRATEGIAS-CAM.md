# GPT-ESCOPO-ESTRATEGIAS-CAM.md

# CaM Project — Escopo de Estratégias de Mercado

**Projeto:** CaM — The Carlos Alternative Money  
**Versão:** 0.1  
**Status:** Documento de análise, estudo, backtest e simulação  
**Natureza:** Uso pessoal, local, não comercial  
**Stack-alvo:** Profit como plataforma operacional + CaM Cockpit local  
**Autor do parecer:** ChatGPT  
**Data:** 2026-05-27

---

## 1. Aviso de escopo e responsabilidade

Este documento não é recomendação individual de investimento, não é consultoria de valores mobiliários, não é oferta pública e não deve ser usado como ordem direta de compra ou venda.

O objetivo é estruturar hipóteses operacionais para o **CaM Lab**, com foco em:

- backtest;
- simulação;
- paper trading;
- controle de risco;
- documentação operacional;
- estudo de estratégias;
- execução futura apenas se validada pelo Risk Engine.

Como o CaM é um projeto pessoal, local e não comercial, a função das estratégias descritas aqui é servir como **matéria-prima de engenharia operacional**, e não como promessa de rentabilidade.

---

## 2. Premissa central

O CaM deve tratar o mercado em três camadas:

```text
1. Camada tática agressiva
   Derivativos: mini índice e mini dólar.
   Objetivo: gerar fluxo controlado com risco limitado.

2. Camada direcional/intermediária
   Swing trade e long/short em ações.
   Objetivo: capturar movimentos de alguns dias ou semanas.

3. Camada patrimonial
   Carteira hard de dividendos.
   Objetivo: acumular patrimônio, renda passiva e estabilidade.
```

A camada agressiva nunca deve ameaçar a camada patrimonial.

A multiplicação patrimonial deve vir da combinação entre:

- preservação de capital;
- assimetria de risco;
- reinvestimento de ganhos;
- disciplina de exposição;
- capacidade de parar;
- conversão de fluxo especulativo em ativos patrimoniais.

---

## 3. Constituição operacional resumida

### 3.1 Limites absolutos

```text
Limite inicial real:
- 1 contrato de mini índice; ou
- 1 contrato de mini dólar.

Limite absoluto futuro:
- 2 contratos de mini índice;
- 2 contratos de mini dólar.
```

Na fase inicial, é proibida operação simultânea de mini índice e mini dólar.

### 3.2 Regras de proteção

```text
- Nunca usar martingale.
- Nunca aumentar mão após loss.
- Nunca operar sem Risk Engine ativo.
- Nunca operar sem journal.
- Nunca operar se o checklist pré-mercado falhar.
- Nunca transformar a carteira hard em margem emocional.
- Nunca operar para recuperar prejuízo histórico.
```

### 3.3 Quantidade operacional sugerida

```text
Fase 0 — Laboratório:
- Backtest ilimitado.
- Simulação ilimitada.
- Nenhum dinheiro real.

Fase 1 — Real mínimo:
- 1 contrato por vez.
- Máximo de 3 operações por dia.
- Máximo de 2 losses consecutivos.
- Stop diário pequeno e pré-definido.

Fase 2 — Real validado:
- 1 contrato por vez.
- Possibilidade de alternar WIN e WDO, sem simultaneidade.
- Aumento apenas se houver histórico estatístico.

Fase 3 — Exposição máxima CaM:
- Até 2 WIN ou até 2 WDO.
- Simultaneidade só após validação estatística específica.
- Exposição máxima nunca pode ser justificada por emoção ou oportunidade.
```

---

## 4. Estratégias de derivativos

As cinco estratégias abaixo foram desenhadas para mini índice e mini dólar, com prioridade de implantação no Profit e validação no CaM Lab.

Ordem recomendada de implementação:

```text
1. No Trade Strategy
2. VWAP Pullback
3. Opening Range Breakout Controlado
4. Trend Day Following
5. Mean Reversion à VWAP
6. Reversão em Exaustão com Bandas
```

A lista contém cinco estratégias operacionais de derivativos. A “No Trade Strategy” é uma estratégia de bloqueio transversal e deve ser implementada antes de todas.

---

# Estratégia 0 — No Trade Strategy

## Natureza

Estratégia de bloqueio, proteção e preservação de capital.

## Objetivo

Impedir operações em cenários onde a vantagem estatística é baixa ou onde o risco operacional está elevado.

## Quando bloquear

```text
- Perda diária atingida.
- Duas perdas consecutivas.
- Spread, volatilidade ou candle anormal.
- Mercado sem direção e sem bordas claras.
- Mercado direcional sem pullback aceitável.
- Preço muito distante da VWAP.
- Falha de conexão.
- Profit instável.
- Estratégia sem confirmação.
- Operador tentando forçar entrada.
- Evento macroeconômico relevante próximo.
```

## Quantidade sugerida

```text
Quantidade de operações permitidas em dia bloqueado: 0
```

## Observação

A melhor estratégia do CaM pode ser não operar. Em derivativos, sobreviver vale mais que acertar uma entrada.

---

# Estratégia 1 — VWAP Pullback

## Natureza

Day trade direcional com pullback.

## Ativos

```text
Preferencial: WIN
Secundário: WDO
```

## Objetivo

Operar a favor do fluxo dominante do dia, usando a VWAP como referência de preço médio institucional.

## Compra

```text
1. Preço acima da VWAP.
2. VWAP inclinada para cima.
3. Preço corrige até VWAP ou média curta.
4. Candle de retomada fecha acima da máxima do candle anterior.
5. Entrada comprada.
```

## Venda

```text
1. Preço abaixo da VWAP.
2. VWAP inclinada para baixo.
3. Preço corrige até VWAP ou média curta.
4. Candle de retomada fecha abaixo da mínima do candle anterior.
5. Entrada vendida.
```

## Stop

```text
- Stop técnico no fundo/topo do pullback; ou
- Stop financeiro máximo definido pelo Risk Engine.
```

## Alvo

```text
- 1R a 1,5R; ou
- alvo fixo validado em backtest; ou
- saída por perda de força.
```

## Quantidade sugerida

```text
Fase inicial: 1 contrato.
Fase validada: até 2 contratos.
Máximo diário: 2 tentativas.
```

## Risco principal

Dia lateral pode gerar falso sinal repetido.

## Filtro obrigatório

Não operar se a VWAP estiver plana e o preço estiver cruzando a VWAP repetidamente.

---

# Estratégia 2 — Opening Range Breakout Controlado

## Natureza

Day trade de rompimento da região inicial do pregão.

## Ativos

```text
Preferencial: WIN
Secundário: WDO, apenas após validação separada
```

## Objetivo

Capturar movimento direcional após definição da máxima e mínima da abertura.

## Construção da range

```text
- Marcar máxima e mínima dos primeiros 15 ou 30 minutos.
- A janela exata deve ser parametrizável no CaM Lab.
```

## Compra

```text
1. Fechamento acima da máxima da range inicial.
2. Preço acima da VWAP.
3. Candle de rompimento sem pavio excessivo.
4. Entrada comprada após confirmação.
```

## Venda

```text
1. Fechamento abaixo da mínima da range inicial.
2. Preço abaixo da VWAP.
3. Candle de rompimento sem pavio excessivo.
4. Entrada vendida após confirmação.
```

## Stop

```text
- Dentro da range; ou
- atrás do candle de rompimento; ou
- stop financeiro máximo do Risk Engine.
```

## Alvo

```text
- Projeção parcial da amplitude da range;
- 1R a 2R;
- saída antecipada se voltar para dentro da range.
```

## Quantidade sugerida

```text
Fase inicial: 1 contrato.
Máximo diário: 1 tentativa por direção.
Máximo total: 2 operações no dia.
```

## Risco principal

Falso rompimento.

## Filtro obrigatório

Não operar se a range inicial for grande demais, pois isso aumenta o stop e reduz a assimetria.

---

# Estratégia 3 — Trend Day Following

## Natureza

Day trade direcional de continuação.

## Ativos

```text
WIN e WDO, com backtests separados.
```

## Objetivo

Evitar reversões contra tendência e operar apenas a favor de dias claramente direcionais.

## Compra

```text
1. Preço acima da VWAP.
2. VWAP inclinada para cima.
3. Médias curtas alinhadas.
4. Fundos ascendentes.
5. Pullback sem perda estrutural.
6. Candle de retomada.
```

## Venda

```text
1. Preço abaixo da VWAP.
2. VWAP inclinada para baixo.
3. Médias curtas alinhadas para baixo.
4. Topos descendentes.
5. Pullback sem rompimento estrutural.
6. Candle de retomada vendedora.
```

## Stop

```text
- Fundo/topo do pullback;
- rompimento da estrutura;
- stop financeiro máximo do Risk Engine.
```

## Alvo

```text
- Continuação até perda de força;
- 1,5R a 2R;
- trailing stop apenas após validação.
```

## Quantidade sugerida

```text
Fase inicial: 1 contrato.
Máximo diário: 2 operações.
Não operar se já perdeu no primeiro trade e o mercado ficou errático.
```

## Risco principal

Entrar tarde, no esgotamento do movimento.

## Filtro obrigatório

Não operar se o preço estiver longe demais da VWAP ou da média curta.

---

# Estratégia 4 — Mean Reversion à VWAP

## Natureza

Day trade de retorno à média.

## Ativos

```text
WIN e WDO, com preferência para cenários laterais.
```

## Objetivo

Capturar retorno parcial à VWAP quando o mercado estiver sem tendência forte e o preço estiver excessivamente afastado.

## Compra

```text
1. VWAP relativamente plana.
2. Preço muito abaixo da VWAP.
3. Sinal de exaustão vendedora.
4. Candle de rejeição ou retorno.
5. Entrada comprada buscando retorno parcial.
```

## Venda

```text
1. VWAP relativamente plana.
2. Preço muito acima da VWAP.
3. Sinal de exaustão compradora.
4. Candle de rejeição ou retorno.
5. Entrada vendida buscando retorno parcial.
```

## Stop

```text
- Atrás do extremo de exaustão;
- stop financeiro máximo;
- bloqueio se o mercado virar trend day.
```

## Alvo

```text
- Retorno parcial à VWAP;
- nunca exigir retorno completo;
- saída se perder força antes da VWAP.
```

## Quantidade sugerida

```text
Fase inicial: apenas simulação.
Depois: 1 contrato.
Máximo diário: 1 tentativa.
```

## Risco principal

Confundir exaustão com início de tendência forte.

## Filtro obrigatório

Proibido operar se a VWAP estiver fortemente inclinada contra a operação.

---

# Estratégia 5 — Reversão em Exaustão com Bandas

## Natureza

Day trade contra movimento extremo.

## Ativos

```text
Somente após validação em laboratório.
Preferencialmente WIN.
```

## Indicadores possíveis

```text
- Bandas de Bollinger;
- RSI;
- distância da VWAP;
- candle de rejeição;
- volume/clímax.
```

## Compra

```text
1. Preço fecha fora da banda inferior.
2. RSI indica sobrevenda.
3. Candle seguinte mostra perda de força vendedora.
4. Entrada apenas após candle de retorno.
```

## Venda

```text
1. Preço fecha fora da banda superior.
2. RSI indica sobrecompra.
3. Candle seguinte mostra perda de força compradora.
4. Entrada apenas após candle de retorno.
```

## Stop

```text
- Atrás da máxima/mínima de exaustão;
- stop financeiro máximo do Risk Engine;
- bloqueio imediato se houver continuação forte contra a entrada.
```

## Alvo

```text
- Retorno parcial à média;
- 1R;
- saída rápida.
```

## Quantidade sugerida

```text
Fase inicial: somente simulação.
Fase posterior: 1 contrato.
Máximo diário: 1 operação.
```

## Risco principal

Pegar faca caindo ou tentar adivinhar topo.

## Filtro obrigatório

Não operar contra trend day claro.

---

## 5. Estratégias Long & Short em ações

## 5.1 Objetivo

Capturar distorções relativas entre dois ativos, reduzindo a dependência direcional do Ibovespa.

Exemplos conceituais:

```text
- ação ON contra PN da mesma empresa;
- banco A contra banco B;
- seguradora A contra seguradora B;
- varejista A contra varejista B;
- empresa forte contra empresa fraca do mesmo setor.
```

## 5.2 Estrutura

```text
Ponta long:
- ativo considerado relativamente mais forte, descontado ou com melhor tendência.

Ponta short:
- ativo considerado relativamente mais fraco, esticado ou com pior tendência.
```

A venda descoberta no Brasil normalmente exige aluguel de ativos. A B3 descreve o empréstimo de ativos como serviço no qual o tomador pode vender os ativos emprestados em uma venda a descoberto, ficando obrigado a devolvê-los conforme o combinado.

## 5.3 Quantidade sugerida

Com capital pequeno, a estratégia deve começar apenas em simulação.

```text
Fase inicial:
- simulação apenas.

Fase real futura:
- 1 par por vez.
- exposição bruta pequena.
- evitar concentração.
- evitar ativos ilíquidos.
```

## 5.4 Critérios de entrada

```text
- correlação histórica relevante;
- spread estatístico esticado;
- divergência técnica clara;
- tese setorial coerente;
- liquidez adequada;
- custo de aluguel conhecido;
- risco de evento corporativo mapeado.
```

## 5.5 Critérios de saída

```text
- spread voltou à média;
- tese perdeu validade;
- custo de aluguel inviabilizou;
- stop de spread atingido;
- evento corporativo alterou a relação.
```

## 5.6 Observação

Long & short parece conservador, mas pode ser sofisticado e perigoso se mal dimensionado. Para o CaM, deve ser tratado como estratégia intermediária, não como ponto de partida.

---

## 6. Estratégias de Swing Trade

## 6.1 Objetivo

Capturar movimentos de alguns dias ou semanas em ações líquidas, com risco menor que day trade alavancado.

## 6.2 Tipos sugeridos

```text
1. Swing de rompimento
2. Swing de pullback em tendência
3. Swing de reversão em suporte/resistência
4. Swing setorial
5. Swing pós-correção em ativo de qualidade
```

## 6.3 Quantidade sugerida

```text
Fase inicial:
- máximo de 2 posições simultâneas.
- risco pequeno por operação.
- sem alavancagem.

Fase validada:
- até 4 posições simultâneas.
- diversificação setorial.
- risco agregado controlado.
```

## 6.4 Regras de entrada

```text
- ativo líquido;
- tendência ou região técnica clara;
- stop definido antes da entrada;
- relação risco/retorno mínima;
- ausência de evento binário relevante não controlado;
- posição compatível com capital.
```

## 6.5 Regras de saída

```text
- stop técnico;
- alvo parcial;
- perda de estrutura;
- realização por tempo;
- deterioração de fundamento;
- necessidade de reduzir risco agregado.
```

## 6.6 Técnica agressiva com governança

A técnica agressiva aceitável no CaM não é aumentar mão sem controle. É buscar assimetria:

```text
- perder pequeno quando errado;
- ganhar múltiplos do risco quando certo;
- operar poucos setups;
- reinvestir parte do ganho;
- não deixar trade vencedor virar perdedor;
- não transformar swing em torcida.
```

---

## 7. Estratégia de Acúmulo para Dividendos

## 7.1 Objetivo

Construir carteira hard produtiva, com foco em renda, estabilidade e reinvestimento.

## 7.2 Princípio

A carteira de dividendos não deve ser uma carteira de apostas. Ela deve ser o cofre patrimonial do CaM.

## 7.3 Quantidade sugerida de ativos

```text
Fase inicial:
- 3 a 5 ativos.

Fase intermediária:
- 6 a 10 ativos.

Fase madura:
- 10 a 15 ativos, se houver capital suficiente para diversificação real.
```

Com pouco capital, diversificar demais pode pulverizar posição sem gerar efeito relevante. Melhor começar com poucos ativos líquidos, bons e acompanháveis.

## 7.4 Classes possíveis

```text
- ações pagadoras de dividendos;
- FIIs de tijolo;
- FIIs de papel com cautela;
- ETFs de renda variável, se fizer sentido;
- renda fixa para caixa e estabilidade.
```

## 7.5 Critérios para ações

```text
- histórico de lucro;
- geração de caixa;
- dívida controlada;
- política de distribuição compreensível;
- governança;
- liquidez;
- setor resiliente;
- preço não absurdamente esticado.
```

## 7.6 Critérios para FIIs

```text
- vacância;
- qualidade dos imóveis ou recebíveis;
- gestão;
- diversificação;
- liquidez;
- histórico de distribuição;
- risco de concentração;
- sensibilidade a juros e inflação.
```

## 7.7 Harvest Rule

Todo ganho tático vindo de derivativos ou swing trade deve alimentar a carteira hard.

Sugestão inicial:

```text
Ganhos líquidos realizados:
- 50% para carteira hard;
- 30% para reserva operacional;
- 20% para impostos, custos e caixa.
```

Em fase mais madura:

```text
Ganhos líquidos realizados:
- 70% para carteira hard;
- 20% para reserva operacional;
- 10% para impostos, custos e caixa.
```

## 7.8 Regra de blindagem

```text
A carteira hard não pode ser vendida para financiar loss em derivativo.
```

---

## 8. Técnicas agressivas aceitáveis no CaM

Agressividade não deve significar irresponsabilidade. Para o CaM, agressividade aceitável significa aumentar eficiência, velocidade de aprendizado e assimetria, não aumentar exposição sem controle.

## 8.1 Pirâmide de agressividade permitida

```text
Nível 1 — Agressivo em estudo
- muito backtest;
- muitas simulações;
- muitas hipóteses;
- nenhum risco real.

Nível 2 — Agressivo em disciplina
- operar pouco;
- cortar rápido;
- registrar tudo;
- revisar tudo.

Nível 3 — Agressivo em assimetria
- buscar setups onde o ganho potencial compense o risco;
- evitar trades de baixa relação risco/retorno.

Nível 4 — Agressivo em reinvestimento
- converter ganhos em patrimônio;
- reaplicar dividendos;
- aumentar carteira hard.

Nível 5 — Agressivo em escala controlada
- só aumentar exposição após estatística validada;
- nunca por euforia.
```

## 8.2 Técnicas proibidas

```text
- martingale;
- all-in;
- dobrar mão após loss;
- usar limite da corretora como se fosse capital;
- vender carteira hard para cobrir trade;
- operar notícia sem plano;
- operar cansado, irritado ou eufórico;
- buscar meta diária obrigatória;
- insistir em dia ruim.
```

---

## 9. Métricas obrigatórias por estratégia

Cada estratégia deve ser medida com:

```text
- taxa de acerto;
- payoff;
- expectativa matemática;
- lucro bruto;
- lucro líquido;
- custos;
- slippage;
- drawdown máximo;
- maior sequência de perdas;
- maior sequência de ganhos;
- resultado por horário;
- resultado por ativo;
- resultado por setup;
- resultado por regime de mercado;
- aderência operacional;
- violações de regra;
- motivo de bloqueio pelo Risk Engine.
```

---

## 10. Backlog técnico para o CaM Cockpit

## 10.1 Módulos obrigatórios

```text
- Strategy Registry
- Risk Engine
- Trade Journal
- Portfolio Ledger
- Tax Ledger
- Profit Adapter
- Backtest Importer
- Simulation Manager
- Harvest Manager
- Kill Switch
- AI Analyst
- AI Auditor
```

## 10.2 Telas sugeridas

```text
- Dashboard operacional
- Estratégias
- Backtests
- Simulação
- Journal
- Carteira hard
- Harvest
- Impostos
- Risk Engine
- Relatórios
```

---

## 11. Roadmap recomendado

```text
Fase 1 — Base
- Implementar ledger.
- Implementar journal.
- Implementar cadastro de estratégias.
- Implementar Risk Engine.

Fase 2 — Laboratório
- Implementar backtest/importação.
- Implementar simulação.
- Medir estratégias sem dinheiro real.

Fase 3 — Profit
- Implementar estratégia no Profit/NTSL.
- Conectar outputs ao CaM.
- Registrar sinais e decisões.

Fase 4 — Real mínimo
- Operar 1 contrato.
- Poucas operações.
- Loss pequeno.
- Sem simultaneidade.

Fase 5 — Patrimônio
- Ativar Harvest Rule.
- Alimentar carteira hard.
- Criar relatório mensal.
```

---

## 12. Conclusão executiva

O CaM deve ser agressivo na engenharia, na disciplina, no aprendizado e no reinvestimento.

Mas deve ser conservador na exposição inicial.

A multiplicação patrimonial sustentável não deve depender de uma única grande operação. Ela deve emergir da soma de:

```text
- edge validado;
- risco pequeno;
- repetição disciplinada;
- reinvestimento inteligente;
- proteção contra ruína;
- carteira hard crescendo com o tempo.
```

O derivativo pode gerar fluxo.

O swing trade pode capturar movimentos maiores.

O long & short pode explorar distorções relativas.

A carteira de dividendos deve proteger o patrimônio produzido.

O Risk Engine deve proteger o operador dele mesmo.

---

## 13. Fontes de referência consultadas

- B3 — Futuro Mini de Ibovespa: especificação do WIN, tamanho do contrato, variação mínima e lote padrão.
- B3 — Futuro Mini de Taxa de Câmbio de Reais por Dólar Comercial: especificação do WDO, tamanho do contrato, cotação, variação mínima e lote padrão.
- B3 — Margem mínima requerida e guia educacional para minicontratos.
- B3 — Empréstimo de ativos: funcionamento do empréstimo de ativos e venda a descoberto.
- Portal do Investidor/Gov.br — Robôs de investimentos e necessidade de autorização CVM quando houver prestação de consultoria automatizada a terceiros.

