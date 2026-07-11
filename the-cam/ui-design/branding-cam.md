# Branding — Cockpit CaM

> Diretrizes de identidade visual e linguagem do cockpit CaM.
> Este documento é agnóstico de framework — aplicável ao frontend do cockpit e a qualquer material visual interno.
> Para cores e tipografia detalhadas, consultar `paleta-cam.md`.
> Para valores e propósito do projeto, consultar `../../CONSTITUICAO.md`.
> Para design tokens e componentes, consultar `design-system.md`.

---

## 1. Identidade Visual

### Nome

**CaM** — *The Carlos Alternative Money*.

Em uso visual, o wordmark usa:

> **C**a**M** — com `a` em tom de apoio e `C`/`M` em âncora.

Direção cromática:

- `CaM` = âncora tipográfica, normalmente em Mist White (dark) ou Esmeralda Deep (light).
- Acento de marca em Esmeralda CAM.
- Founder Orange pode aparecer como spark editorial (assinatura de Carlos, o operador), nunca como acento fixo do wordmark.

### Natureza

CaM **não é uma empresa, produto ou marca comercial**. É um cockpit pessoal de operação disciplinada de mercado. A identidade visual existe para servir clareza operacional e defesa de capital — não para projetar imagem de mercado.

### Símbolo

- **Símbolo:** mira / crosshair (alvo de precisão) — instrumento de operação focada.
- **Significado:** disciplina, foco, decisão sob risco controlado.
- **Direção visual:** símbolo em Esmeralda Signal/Light sobre fundo Esmeralda Void ou Graphite.
- **Uso de Founder Orange:** permitido como faísca secundária, especialmente em notas pessoais do operador.

---

## 2. Tom de Voz

| Atributo | Descrição |
|---|---|
| Direto | Linguagem clara, sem ornamento; o cockpit informa, não vende |
| Disciplinado | Comunica regra, limite e estado — não opinião |
| Preciso | Números exatos, sempre líquidos (Art. 25º), sem arredondar a favor |
| Sóbrio | Sem euforia em ganho, sem dramatização em perda |
| Defensivo | Quando em dúvida, a UI comunica o que preserva mais capital (Art. 6º) |

---

## 3. Princípios Visuais

### 3.1 Fundamentos

- **Esmeralda CAM é o sistema operando** — clareza, instrumento de precisão, estado sob controle.
- **Founder Orange é faísca** — assinatura pessoal de Carlos, o operador.
- **Dark Mode First** — o cockpit nasce em fundo escuro (sessões longas de tela) e adapta para claro.
- **Tonal layering** — profundidade por variação de superfície, não por sombra pesada.
- **Sem pretos absolutos** — usar Graphite/Esmeralda Void em vez de `#000`.
- **Mobile-aware** — o cockpit prioriza desktop (operação), mas telas de consulta e alerta funcionam em mobile.
- **WCAG AA obrigatório** — validar contraste em todas as combinações; em cockpit operacional, legibilidade é defesa.

### 3.2 Elementos Visuais Recorrentes

| Elemento | Função |
|---|---|
| Mira / crosshair | Foco, disciplina, decisão sob risco |
| Esmeralda Signal | Acento digital, foco, highlights e microinterações |
| Graphite + Esmeralda Void | Base dark do cockpit |
| Founder Orange | Spark editorial, assinatura do operador |
| Cards densos | Organização de dados operacionais, clareza |
| Números grandes | Comunicação direta de métricas — sempre líquidas |

---

## 4. Padrões de Layout

### 4.1 Grid e Responsividade

- **Abordagem:** Desktop-first para telas operacionais; mobile-aware para consulta/alerta.
- **Breakpoints:** 768px (tablet), 1024px (desktop).
- **Container:** largura máxima com padding horizontal responsivo.
- **Grid:** 1 coluna (mobile) -> 2 colunas (tablet) -> 3+ colunas (desktop).

### 4.2 Espaçamentos

| Contexto | Padrão |
|---|---|
| Seções | Padding vertical equivalente a 64-96px |
| Cards | Padding interno de 24-32px |
| Gaps entre elementos | 16px, 24px ou 32px conforme hierarquia |

---

## 5. Padrões de Componentes

### 5.1 Botões

- **Border radius:** 4px para ações; 6px em cards/containers.
- **Transições:** ~200ms em hover, focus e active.
- **Focus:** ring visível em Esmeralda Signal.
- **Active:** escala sutil 98% para feedback tátil.
- **Primary:** Esmeralda Core/CAM conforme contraste.
- **Destructive (kill switch, ações de loss):** Vermelho `#EF4444`, sempre com confirmação.
- **Founder:** Founder Orange apenas em notas/ações editoriais do operador.

### 5.2 Header

- **Comportamento:** sticky, com tonal layering.
- **Wordmark:** `CaM`, com acento Esmeralda.
- **Banner de modo:** indicador **DEMO / REAL** sempre visível (Art. 19º).
- **Kill switch:** acessível a partir do header em telas operacionais (Art. 18º).
- **Mobile:** menu simplificado, touch target mínimo 44x44px.

### 5.3 Footer

- **Fundo:** Esmeralda Void ou Graphite Black.
- **Conteúdo:** wordmark + estado de sessão.
- **Títulos de seção:** Esmeralda Light/Signal, uppercase quando usado como metadado.

### 5.4 Cards

- **Fundo:** Carbon Slate / surface do DS.
- **Sombra:** mínima; preferir borda e tonal shift.
- **Hover:** borda Esmeralda Soft/Signal controlada.
- **Padding:** 24-32px.
- **Cards de resultado:** valor sempre **líquido** de imposto provisionado (Art. 25º).

### 5.5 Painéis de Estado

- **Estado normal:** Esmeralda Void + halos Esmeralda Soft.
- **Bloqueio Risk Engine:** comunicação inequívoca, vermelho/atenção (Art. 15º).
- **Nota do operador:** pode usar Founder Orange como assinatura.

---

## 6. Estados Interativos

| Estado | Comportamento |
|---|---|
| Hover (botões) | Escurecer Esmeralda Core ou elevar tonalmente |
| Hover (cards) | Borda Esmeralda Soft/Signal |
| Hover (links) | Underline + Esmeralda Signal |
| Focus | Ring visível em Esmeralda Signal |
| Active | Escala 98% para feedback tátil |
| Disabled | Opacidade reduzida, cursor not-allowed |
| Bloqueado (Risk Engine) | Ação destrutiva indisponível, mensagem explícita |

---

## 7. Acessibilidade

- Focus ring visível em todos os elementos interativos.
- Contraste WCAG AA validado conforme `paleta-cam.md` e `tokens.md`.
- Links com underline em hover.
- Transições suaves para conforto visual em sessões longas.
- Alternativa textual para ícones decorativos.
- **Cor nunca é único indicador** — crítico em loss/sucesso/bloqueio: usar ícone + texto + cor.

---

## 8. Narrativa de identidade

> O cockpit CaM é um instrumento de precisão a serviço de uma única regra: preservar capital.
> A Esmeralda CAM representa o sistema operando — claro, sóbrio, sob controle.
> O Founder Orange é a faísca de Carlos, o operador: assinatura pessoal, nunca a voz do sistema.
