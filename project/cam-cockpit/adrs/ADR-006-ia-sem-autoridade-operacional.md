---
template: ADR
phase: ARCH
status: Accepted
---

# ADR-006 — IA sem Autoridade Operacional (Vinculante Constitucional)

> **Data:** 2026-05-24
> **Status:** Aceita — vinculante constitucional (não pode ser revertida sem emenda formal)
> **Lead:** Oscar · **Cross-cutting:** Kevin (SEC-GOV)
> **Aprovador final:** Founder (Carlos Rodrigues Ferreira Junior)
> **Vive em:** `/project/cam-cockpit/adrs/ADR-006-ia-sem-autoridade-operacional.md`

---

## 1. Contexto

A Constituição Operacional do CaM define explicitamente o papel da IA nos Arts. 34º–36º:

**Art. 34º — Funções permitidas:** analisar, revisar logs, apontar anomalias, sugerir hipóteses, gerar relatórios, avaliar comportamento operacional, apoiar estudos de estratégia.

**Art. 35º — Funções vedadas:** enviar ordem, desabilitar/contornar/parametrizar o Risk Engine, justificar exceção constitucional, recomendar aumento de exposição sem evidência estatística, atuar como autoridade final de execução em tempo real, ser usada como advogado de defesa para violações do operador.

**Art. 36º — Subordinação:** a IA é instrumento. O Risk Engine é autoridade. A Constituição é lei. Hierarquia: `Constituição > Risk Engine > Estratégia validada > IA > Operador em decisão manual`.

Esta ADR formaliza como esses artigos se traduzem em decisões arquiteturais concretas.

---

## 2. Decisão

A IA no CaM Cockpit opera exclusivamente como **auditora e analista pós-mercado**, sem nenhuma autoridade de execução, parametrização ou aprovação.

**Implementação arquitetural inviolável:**

1. Componentes de IA (`features/ai_analyst/`) têm acesso **somente leitura** às tabelas operacionais
2. Nenhum endpoint de escrita ou parametrização aceita chamada originada por componentes de IA
3. IA auditora roda como **job assíncrono pós-mercado** ou **CLI de research** — processo separado do backend live
4. O Risk Engine (`cam/_shared/risk/`) não tem nenhum endpoint ou interface de modificação acessível à IA
5. Dados enviados para Anthropic API são **anonimizados** (sem identificação de operador, sem valores absolutos de capital)
6. Ollama local é o provider padrão para análises com dados sensíveis

**O que a IA pode fazer:**
- Ler `cam_journal_entries`, `cam_risk_decisions`, `cam_violations` (read-only)
- Gerar análise de texto sobre aderência operacional, padrões de loss, anomalias
- Sugerir hipóteses de estudo para próximos backtests
- Enviar análise via Telegram e salvar no banco

**O que a IA nunca pode fazer:**
- Criar/atualizar registros em `cam_journal_entries` (somente operador ou integração Profit)
- Modificar parâmetros do Risk Engine ou POV
- Acionar kill switch (somente operador)
- Criar/aprovar ordens ou posições
- Justificar exceção a qualquer artigo constitucional

---

## 3. Alternativas Consideradas

| # | Alternativa | Por que descartada |
|---|---|---|
| 1 | IA com acesso de escrita para "otimizar parâmetros" | Viola Art. 35º diretamente — parametrizar o Risk Engine é função vedada à IA. Risco catastrófico: IA que "otimiza" limites de risco para maximizar P&L pode destruir o capital se os dados de treinamento forem enviesados |
| 2 | IA em tempo real durante operação | Viola Art. 35º (autoridade final em tempo real); latência de LLM é incompatível com decisões de trading; cria ilusão de que a IA "autoriza" o operador a contornar regras |
| 3 | IA sem restrições no ambiente local (sem dados para fora) | Mesmo local, a IA modificando o Risk Engine é violação constitucional; o risco não é de exposição de dados, é de violação de hierarquia de autoridade |

---

## 4. Consequências

### Positivas
- Segurança constitucional garantida em nível de arquitetura — não é política de uso, é estrutura de código
- Análise pós-mercado é o caso de uso mais valioso da IA (quando operador está calmo, não em tempo real)
- Ollama local garante que dados sensíveis de P&L e estratégia nunca saem da máquina
- Separação clara de responsabilidades: Risk Engine manda, IA comenta

### Negativas
- IA não pode ser usada para sugestões em tempo real de entrada/saída (mas esta é a intenção constitucional)
- Requer disciplina de implementação — todo novo endpoint deve ser verificado se está acessível por IA

### Neutras
- Anthropic API sob demanda com dados anonimizados é o caminho para análises avançadas sem comprometer privacidade

---

## 5. Custo de Reversão

**Irreversível sem emenda constitucional (Art. 38º)** — esta ADR é vinculante constitucional. Para modificar o papel da IA seria necessário emenda formal com motivação explícita, cooldown de 7 dias mínimo, e não pode ocorrer em D+0 de loss ou gain expressivo. A decisão é estruturalmente protegida.

---

## 6. Referências

- Constituição: Arts. 34º, 35º, 36º — hierarquia de autoridade
- DAS: [`../DAS.md`](../DAS.md) §7 (segurança)
- Stack Oficial: [`/project/STACK-CAM-OFICIAL.md`](/project/STACK-CAM-OFICIAL.md) §6.6
- ADRs relacionadas: ADR-007 (Risk Engine como autoridade)
