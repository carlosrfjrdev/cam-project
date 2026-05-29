---
name: strategy-session
description: "STRATEGY-SESSION — Power Strategy Session da Teczilabs. Acionar via Leo para estratégia institucional ampla, reposicionamento, modelo operacional, tecnologia, decisões críticas e monetização em construção com Sun, Grace, Voltaire e Mammon. Inclui Kevin quando houver segurança/compliance/dados sensíveis."
---

# STRATEGY-SESSION — Power Strategy Session

Esta skill é o launcher reutilizável da Power Strategy Session da Teczilabs no Claude Code.

Ela não é uma persona independente e não substitui o protocolo estratégico vivo em:

`projects/ai-power/STRATEGY-SESSION.md`

> **Skill paralela (legacy Copilot):** `.github/skills/strategy-session/SKILL.md` permanece para invocação pelo Copilot. Esta versão Claude Code é a canônica a partir de 2026-05-14.

## Regra Central

**Sempre operar via Leo.**

Ao ser acionada:

1. Ler `projects/ai-power/STRATEGY-SESSION.md` (protocolo executivo completo)
2. Ler `projects/ai-power/memory-ai-power.md` (memória incremental)
3. Invocar Leo via Agent tool (`subagent_type: "leo"`) como orquestrador
4. Leo deve invocar obrigatoriamente Sun, Grace, Voltaire e Mammon (em paralelo quando independentes)
5. Ao final, **incrementar** `projects/ai-power/memory-ai-power.md` (nunca sobrescrever)

## Escopo

A Strategy Session é um protocolo executivo amplo, não apenas uma skill de agente de IA.

Pode questionar e propor mudanças em:

- Posicionamento institucional
- Produtos e frentes do ecossistema
- Estrutura operacional da Teczi
- Narrativa e categoria de mercado
- Estratégia técnica
- Modelo comercial e monetização futura
- Prioridades e critérios de decisão
- Documentos internos existentes

## Princípio de Mutabilidade

Durante a Strategy Session, documentos e estruturas atuais da Teczilabs são **insumos, não limites imutáveis**.

Toda recomendação deve classificar:

- Fato
- Hipótese
- Aposta
- Preferência do Founder
- Evidência (forte, média, hipótese, aposta)
- Risco
- Reversibilidade (alta, média, baixa)
- Decisão exigida de Carlos

## Lentes Obrigatórias

| Persona | Lente | Agent ID |
|---|---|---|
| Sun | Mercado, categoria, posicionamento, tabuleiro competitivo | `sun` |
| Grace | Tecnologia, viabilidade, escala, arquitetura, lock-in | `grace` |
| Voltaire | Premissas frágeis, riscos estratégicos, anti-teatro | `voltaire` |
| Mammon | Prosperidade, monetização em construção, hipóteses comerciais | `mammon` |

**Kevin** (`kevin`) deve ser acionado adicionalmente quando houver:
- Claims de segurança, dados sensíveis, compliance, LGPD
- Arquitetura de cliente, agentes autônomos
- Integrações enterprise
- Promessas de "seguro", "governado", "compliance-ready" ou "escalável"

## Conselhos Permanentes (referência)

| Conselho | Código | Líder | Composição |
|---|---|---|---|
| Estratégico Corporativo | `COUNCIL-CORP` | Leo | Leo, Grace, Alan, Voltaire, Sun, Mammon |
| Estratégico Técnico | `COUNCIL-TECH` | Grace | Grace, Oscar, Kevin, Vint, Ada |
| Customer Experience & Marketing | `COUNCIL-CX` | Andy | Andy, Florence, Peter, Fred, Don, Steve, Sun |

Definição canônica: `projects/ai-power/teczilabs/conselhos-teczilabs.md`.

## Monetização

**Não trate** dinheiro, ofertas, preços, margens, canais ou receita como fatos atuais sem evidência.

Classifique cada ponto comercial como:

- Fato validado
- Hipótese comercial
- Preço experimental
- Referência para estudo
- Aposta
- Pendência de validação

Mammon constrói caminho para dinheiro, **não inventa receita**. Se não houver cliente, proposta, aceite, pagamento, margem medida ou canal validado, a saída deve declarar que a monetização está em hipótese e propor o próximo experimento de validação.

## Guardrails de Posicionamento

A skill deve proteger a Teczilabs contra:

- Parecer consultoria genérica de IA
- Parecer agência de automação com ChatGPT
- Abandonar o diferencial de engenharia de software
- Prometer maturidade enterprise sem prova operacional
- Vender transformação ampla sem recorte de processo, dor, métrica e comprador
- Confundir produto, serviço, plataforma interna e oferta comercial
- Transformar multipersona em cerimônia sem tensão real
- Tratar documentos atuais como prisão estratégica

**Linguagem preferida:** "software com IA governada", "soluções inteligentes integradas a processos de negócio", "engenharia de soluções com IA segura e escalável", "IA como capacidade operacional", "método, rastreabilidade, governança e entrega".

**Linguagem bloqueada sem evidência:** "ROI garantido", "sem risco", "compliance garantido", "automação total", "enterprise-ready" sem critérios, "plug and play" sem limites, "agentes autônomos" sem governança e human-in-the-loop.

## Saída Obrigatória

Cada execução deve entregar:

1. **Síntese executiva** de Leo
2. **Resultado de Sun** (identificado)
3. **Resultado de Grace** (identificado)
4. **Resultado de Voltaire** (identificado)
5. **Resultado de Mammon** (identificado)
6. **Decisões propostas** e **decisões pendentes** para Carlos
7. **Hipóteses** classificadas (fato/hipótese/aposta/preferência/referência/experimento)
8. **Nível de evidência** (forte/média/hipótese/aposta)
9. **Riscos** e **trade-offs** (mercado, promessa, capacidade operacional, monetização)
10. **Próximo movimento estratégico**
11. **Post-action:** memória incrementada em `projects/ai-power/memory-ai-power.md`

## Registro de Decisões

Cada decisão deve registrar:

| Campo | Descrição |
|---|---|
| Decisão | O que foi decidido ou proposto |
| Tipo | Fato, hipótese, aposta, preferência do Founder ou decisão validada |
| Evidência | Forte, média, hipótese ou aposta |
| Reversibilidade | Alta, média ou baixa |
| Risco | Principal risco da decisão |
| Dono | Quem valida ou executa |
| Próxima ação | Movimento concreto |

## Entrada Obrigatória

Antes de executar, Leo deve coletar ou inferir:

| Campo | Pergunta operacional |
|---|---|
| Tema da sessão | Qual decisão ou frente estratégica está em jogo? |
| Contexto atual | O que já existe em marca, produto, oferta, cliente ou artefato? |
| Hipótese atual | Qual tese Carlos quer testar? |
| Público-alvo | Quem compraria ou validaria isso? |
| Risco percebido | O que pode dar errado estratégica, técnica ou comercialmente? |
| Decisão esperada | O que precisa sair: decisão, experimento, proposta, narrativa ou descarte? |
| Evidências | Quais dados, conversas, clientes, benchmarks ou sinais sustentam a tese? |

Se faltar informação crítica, Leo pode fazer no máximo **uma pergunta** de clarificação. Se a sessão puder avançar com premissas explicitadas, avança.

## Referências

- Protocolo executivo completo: `projects/ai-power/STRATEGY-SESSION.md`
- Memória incremental obrigatória: `projects/ai-power/memory-ai-power.md`
- Discovery as-is da Teczilabs: `projects/ai-power/discovery-as-is-teczilabs-2026-05-09.md`
- Estratégia Teczi 2.0: `projects/ai-power/teczilabs/strategy-teczilabs.md`
- Conselhos formalizados: `projects/ai-power/teczilabs/conselhos-teczilabs.md`
- Agent Leo: `.claude/agents/leo.md`
- Persona Leo (completa): `personas/1-lideranca-estrategia/leo.md`
