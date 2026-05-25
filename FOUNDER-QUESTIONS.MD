# FOUNDER-QUESTIONS — cam-cockpit

> **Data de criação:** 2026-05-24
> **Contexto:** Perguntas não-bloqueantes levantadas durante a produção dos artefatos PDOC → DISC → ARCH → SPEC
> **Instrução:** Carlos responde ao final — nenhuma dessas perguntas bloqueou a produção dos artefatos

---

## F1 — Integração Profit / Plataforma

### FQ-001 — Versão do Profit: Pro ou Ultra?

**Contexto:** O STACK-CAM-OFICIAL.md menciona "Profit Pro ou Ultra" como variável em aberto.
O módulo de **Automação de Estratégias** (necessário para Fase F4 de integração com conta real automatizada) está disponível no Pro ou somente no Ultra?

**Impacto:** Define se Carlos precisa contratar upgrade para chegar na Fase F4. Não bloqueia a Fase 0 (que opera sem automação real).

**Resposta do Founder:** Variável se mantem aberta até F4... mas vamos criar em cima de profit pro por enquanto.

---

### FQ-002 — Corretora vinculada ao Profit

**Contexto:** A corretagem por mini contrato impacta diretamente o edge mínimo de sobrevivência do CaM.
O STACK-CAM-OFICIAL.md §10 (Voltaire) alerta: os custos de plataforma representam R$ 200–380/mês = 4–8% sobre R$ 5.000. Isso é o edge mínimo que a estratégia precisa bater para não queimar caixa pessoal.

**Pergunta:** Qual corretora está (ou será) vinculada? (XP? Clear? Rico? Outra?)

**Impacto:** Entra no cálculo de corretagem no ledger fiscal e no backtest (backtests sem corretagem real são honestos para Carlos mas desonetos para a estratégia). Não bloqueia Fase 0.

**Resposta do Founder:** Considere corretagem 0 e procurarei corretora com profitpro gratis.

---

### FQ-003 — Fonte de tick histórico para backfill inicial

**Contexto:** O M2 do roadmap prevê backfill de tick histórico na TimescaleDB para os primeiros estudos de padrão (META: 1–2 anos de histórico para WIN e WDO).

**Pergunta:** O Profit exporta tick raw (em granularidade de ms)? Ou apenas candles em timeframes fixos (1m, 5m)?

**Impacto:** Define a estratégia de backfill da Timescale no M2:
- Se Profit exporta tick → importa via CSV/Parquet direto
- Se Profit exporta apenas candles → precisa de fonte alternativa de tick histórico (Tickstory, Dukascopy, outras)
- Se apenas candles estão disponíveis → backtest opera em candles, não em tick puro

Não bloqueia Fase 0, bloqueia M2.

**Resposta do Founder:** Precisamos encontrar meio de isto ser automatizado. vamos pelo tick raw e candles em timeframe nas analises.

---

## F2 — Estratégia e Edge

### FQ-004 — Tese de edge da primeira estratégia

**Contexto:** O STACK-CAM-OFICIAL.md §13 (bloqueadores Fase 1) lista este item como pendente.
Sem tese de edge definida, a Fase 0 constrói infra completa mas sem destino para o backtest engine (M6) e para o módulo de pattern studies (M7).

**Pergunta:** Qual é a hipótese de edge da primeira estratégia que Carlos pretende validar no backtest? (Exemplos: reversão à média em horário específico? Breakout de abertura? Tendência de fundo com filtro de volatilidade? Outro?)

**Impacto:** Não bloqueia Fase 0, bloqueia M6 (backtest) e M7 (pattern studies). A infraestrutura é válida independente da estratégia.

**Resposta do Founder:** Ainda não temos estratégia virá de estudo posterior.

---

### FQ-005 — Definição técnica de Setup A+ (Fase 4)

**Contexto:** O Art. 11º permite 2 contratos SOMENTE em Setup A+ na Fase 4. A POV v1.0 (Anexo III da Constituição) define: "A definir após Fase 3. Requer confluência de pelo menos 3 fatores objetivos (volatilidade, tendência de fundo, horário, contexto macro, etc.). Critério escrito, auditável e congelado em POV antes de uso real."

**Pergunta:** Carlos tem hipótese inicial de quais fatores comporiam o Setup A+? (Não precisa ser definitivo agora — é apenas para informar o design do feature `strategies/` no backend.)

**Impacto:** Não bloqueia nenhuma das fases 0–3. Bloqueia apenas a funcionalidade Setup A+ do Risk Engine (validator `setup_a_plus_check`) que é Fase 4.

**Resposta do Founder:** Ainda não tenho estratégia.. preciso de analises e recomendações

---

## F3 — Parâmetros Operacionais Iniciais

### FQ-006 — Confirmação dos parâmetros de stop loss da POV

**Contexto:** A POV v1.0 (Anexo III) define como "parâmetros de estratégia, ajustável por backtest":
- WIN: stop 150–250 pontos
- WDO: stop 3–7 pontos

Esses valores são os intervalos da POV — o backtest vai refinar. Mas para o Risk Engine implementar o `trading_window_check` e o mapa de risco, precisamos saber se Carlos confirma esses valores como ponto de partida inicial.

**Pergunta:** Os stops padrão da POV (150–250p WIN / 3–7p WDO) estão corretos como ponto de partida para o backtest?

**Resposta do Founder:** Foco em Win stops estão adequados

---

### FQ-007 — Capital efetivo da corretora no início da Fase 0

**Contexto:** A Constituição define R$ 5.000 de capital declarado em três buckets. Mas na Fase 0 (Construção) ainda não há capital depositado na corretora.

**Pergunta:** O capital de R$ 5.000 está depositado na corretora agora (mesmo que bloqueado para operação na Fase 0)? Ou será depositado somente ao entrar na Fase 1 (Paper Trading)?

**Impacto:** Afeta o estado inicial dos buckets no ledger e o cálculo de limites de loss do Risk Engine (que opera sobre o capital declarado total, não o capital na corretora). Não bloqueia Fase 0 tecnicamente, mas a DAS e o ledger assumem R$ 5.000 como base dos cálculos.

**Resposta do Founder:** será depositado quando eu informar, mas pode-se iniciar com este valor para calculos

---

## F4 — Infraestrutura e Ambiente

### FQ-008 — Credenciais e secrets iniciais

**Contexto:** O cockpit precisa de:
- String de conexão PostgreSQL (local, definida pelo operador)
- Token do Telegram Bot (precisa criar um bot em @BotFather)
- Chat ID do Telegram do operador
- (futuro) Anthropic API key

**Pergunta:** Carlos já criou o bot no Telegram? Se não, precisa de orientação para criar via @BotFather?

**Impacto:** Não bloqueia o desenvolvimento — apenas bloqueia os testes de integração com Telegram. O sistema funciona em modo degradado sem Telegram configurado.

**Resposta do Founder:** Não criei o bot, nem tenho knowhow para fazer isto preciso de TODO infra necessário

---

### FQ-009 — Path de backup local (Windows + Google Drive)

**Contexto:** O sistema prevê `pg_dump` diário + `rclone` para Google Drive.

**Pergunta:** Carlos tem Google Drive configurado e espaço disponível? Ou prefere S3 / outro destino de backup?

**Impacto:** Apenas configura o destino do `rclone`. Não bloqueia desenvolvimento.

**Resposta do Founder:** tenho gdrive sim... preciso de todo de configuração

---

## F5 — Decisões Pendentes da Stack

### FQ-010 — MT5 como fallback: decisão final

**Contexto:** O STACK-CAM-OFICIAL.md marca como "decisão pendente": Carlos vai escolher entre a variante Windows+Profit (este SPEC) OU a variante Linux+MT5 (documentada em `STACK-CAM-OFICIAL-LINUX.MD`).

**Pergunta:** A decisão foi tomada em favor do Windows+Profit (que é o que este SPEC especifica)? Ou Carlos ainda está avaliando a variante Linux+MT5?

**Impacto:** Se a decisão for Linux+MT5, este SPEC inteiro precisa ser revisado (ADRs de integração, OS de produção, etc.). Esta é a única pergunta que pode tornar-se BLOQUEANTE se a resposta for "MT5".

**Resposta do Founder:** windows first. Não mt5 por enquanto, somente se eu achar adequado vamos.. mas não bloqueie considere windows

---

### FQ-011 — Schedule de revisão da stack

**Contexto:** STACK-CAM-OFICIAL.md §13 item 6: "quando reavaliar versões, modelo IA, etc."

**Pergunta:** Carlos quer definir um gatilho para revisão de versões da stack? (Ex: a cada release de Fase, a cada 6 meses, somente quando houver breaking change?)

**Impacto:** Apenas governa a cadência de atualização de dependências. Não bloqueia nada agora.

**Resposta do Founder:** Revisarei nas fases.. modelo de ia openai por enquanto pois ja tenho creditos, claude secundário... não tenho maquina e capacidade para modelos locais.

---

## Resumo das Perguntas por Urgência

| FQ# | Pergunta | Bloqueia |
|---|---|---|
| FQ-010 | MT5 vs Profit — decisão final | ARCH/SPEC inteiros se resposta for MT5 |
| FQ-003 | Fonte de tick histórico | M2 (backfill Timescale) |
| FQ-004 | Tese de edge da estratégia | M6 (backtest), M7 (pattern studies) |
| FQ-001 | Profit Pro vs Ultra | M8 (integração F4) |
| FQ-002 | Corretora vinculada | Cálculo de edge no backtest |
| FQ-005 | Setup A+ composição inicial | Feature setup_a_plus_check (Fase 4) |
| FQ-006 | Confirmação stops padrão POV | Parâmetros iniciais do Risk Engine |
| FQ-007 | Capital na corretora agora? | Estado inicial do ledger |
| FQ-008 | Bot Telegram criado? | Testes de integração Telegram |
| FQ-009 | Google Drive disponível? | Configuração de backup |
| FQ-011 | Schedule revisão stack | Governança de dependências |

---

> **Nota de Leo:** A FQ-010 é a única que pode virar BLOQUEANTE. Se Carlos confirmar Windows+Profit (que é a hipótese deste documento), todas as outras são não-bloqueantes e podem ser respondidas ao longo da Fase 0.
