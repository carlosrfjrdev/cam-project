# Paleta Visual — Cockpit CaM

> Filosofia de cor, princípios visuais e diretrizes de uso do cockpit CaM.
> Este documento descreve **como e quando** usar as cores.
> Para valores atômicos e implementação, consultar `tokens.md`.
> Para identidade visual e padrões de componentes, consultar `branding-cam.md`.
> Para o propósito e os limites do projeto, consultar `../../CONSTITUICAO.md`.

---

## 1. Direção cromática

O cockpit CaM adota a direção **Esmeralda CAM** como paleta institucional de referência do Design System.

A semântica de cor é organizada em camadas:

| Camada | Cor | Significado |
|---|---|---|
| Identidade do cockpit | Esmeralda CAM | Sistema operando, clareza, instrumento de precisão |
| Operador | Founder Orange | Assinatura pessoal de Carlos, notas e destaques editoriais |
| Resultado positivo | Success Green | Ganho líquido, operação concluída OK, status positivo |
| Risco / loss / destrutivo | Vermelho Alerta | Perda, ação destrutiva, bloqueio do Risk Engine, kill switch |

Regra central:

> **Esmeralda CAM é a identidade do cockpit, não o verde financeiro de resultado. Ganho/loss usam as cores funcionais (`#10B981` / `#EF4444`), nunca a Esmeralda institucional.**

A separação é defesa de capital (lente Don): o operador nunca pode confundir "cor de marca" com "estou no positivo". Resultado é sempre lido pelas cores funcionais e sempre **líquido** de imposto provisionado (Art. 25º).

---

## 2. Paleta Esmeralda CAM

> Valores de referência para documentação e prototipação. A consolidação em tokens de implementação ocorre em `tokens.md`.

| Nome | Hex | Uso |
|---|---:|---|
| Esmeralda Void | `#061711` | Fundo profundo do cockpit, painéis dark e áreas de identidade |
| Esmeralda Deep | `#071A12` | Base escura com matiz de marca |
| Esmeralda Night | `#0B2418` | Surface escura tematizada |
| Esmeralda Core | `#047857` | Primária institucional sóbria |
| Esmeralda CAM | `#059669` | Primária viva para identidade, CTAs e acentos |
| Esmeralda Signal | `#10B981` | Brilho digital, foco, microinterações e highlights controlados |
| Esmeralda Light | `#34D399` | Acentos luminosos em dark mode |
| Esmeralda Soft | `rgba(5,150,105,0.14)` | Fundos tonais, badges e halos |

> **Nota:** `Esmeralda Signal` (`#10B981`) coincide em hex com o `Success Green` funcional. No cockpit, o significado vem do contexto: como acento de identidade em microinteração vs. como status de sucesso/ganho. **Cor nunca é único indicador** — sucesso/ganho sempre acompanham ícone + texto.

### 2.1 Uso recomendado

| Contexto | Cor |
|---|---|
| Wordmark em dark mode | `CaM` em `#F8FAFC`, acento em Esmeralda Light ou Signal |
| Wordmark em light mode | `CaM` em Esmeralda Deep, acento em Esmeralda Core |
| CTA primário | Esmeralda CAM/Core, conforme contraste |
| Links e focus ring | Esmeralda Signal |
| Painel dark do cockpit | Esmeralda Void + halos Esmeralda Soft |
| Badges de identidade | Esmeralda Soft + Esmeralda Light |
| Fundos extensos | Esmeralda Void/Deep, nunca Esmeralda Signal |

### 2.2 Proibições

- Usar Esmeralda CAM como indicador de ganho, saldo positivo ou resultado de operação — isso é função das cores funcionais.
- Usar verde com imagens de folha, natureza, sustentabilidade ou saúde.
- Usar verde como único indicador funcional (Art. cromático de defesa: cor + ícone + texto).
- Usar Esmeralda Signal em textos longos ou fundos extensos.

---

## 3. Neutros de apoio

| Nome | Hex | Uso |
|---|---:|---|
| Graphite Black | `#09090B` | Base dark sem preto absoluto |
| Lab Graphite | `#111827` | Superfície principal |
| Carbon Slate | `#1F2937` | Cards e blocos |
| Steel Muted | `#64748B` | Texto secundário |
| Cloud Gray | `#E5E7EB` | Bordas e detalhes leves |
| Mist White | `#F8FAFC` | Texto claro e fundos light |

---

## 4. Founder Orange

O **Founder Orange** é o acento editorial pessoal de Carlos, o operador do cockpit.

| Nome | Hex | Uso |
|---|---:|---|
| Founder Orange | `#FF7A00` | Assinatura do operador, notas pessoais, destaques editoriais |
| Founder Ember | `#C2410C` | Versão profunda e editorial |
| Founder Glow | `#FDBA74` | Brilho pontual, transições e microdetalhes |

Regra narrativa:

> **A Esmeralda é o sistema operando. O laranja é a voz pessoal do operador — nunca a voz do sistema.**

### 4.1 Onde usar

- Notas e anotações do operador no journal.
- Destaques editoriais em telas de revisão/post-mortem.
- Marcação de decisão manual do operador (Art. 36º — operador em decisão manual).
- Pequenos sparks em telas de identidade.

### 4.2 Onde não usar

- CTA primário padrão do cockpit.
- Cor funcional de warning, loss ou bloqueio.
- Fundos extensos.
- Indicadores de resultado financeiro.
- Elementos que competem com a Esmeralda CAM.

Referência detalhada: `paleta-founder.md`.

---

## 5. Cores funcionais e defesa de capital

As cores funcionais carregam significado operacional crítico — são lidas pelo operador em decisão sob risco. Sua separação da identidade é inegociável (lente Don).

| Função | Cor | Token | Regra |
|---|---|---|---|
| Sucesso / ganho líquido | `#10B981` | `--success` | Sempre com ícone + texto; valor líquido (Art. 25º) |
| Loss / destrutivo / kill switch | `#EF4444` | `--destructive` | Confirmação obrigatória em ações; bloqueio explícito |
| Atenção / warning | `#F59E0B` | `--warning` | DARF pendente, limite próximo, modo demo |
| Informação / IA | `#0EA5E9` | `--info` | Saídas de IA (auditora, nunca executora — Arts. 34º-36º) |

Regras:

- **Líquido sempre visível** — resultado bruto nunca substitui o líquido provisionado (Art. 25º).
- **Bloqueio do Risk Engine** comunicado em vermelho/atenção, inequívoco (Art. 15º).
- **Kill switch** em vermelho destrutivo, acessível sem fricção (Art. 18º).

---

## 6. Tipografia

> Escala completa e responsividade: `tokens.md` (seção 3).

- **Headings:** Poppins, Semibold (600)
- **Body:** Inter, Regular (400)
- **Números operacionais:** Inter com tabular figures quando disponível, para alinhamento de colunas de valores.

---

## 7. Uso de fundos

> Valores de superfície e hierarquia completa: `tokens.md` (seção 2).

O cockpit é **Dark Mode First**.

Regras:

- Fundos profundos usam Graphite Black, Lab Graphite ou Esmeralda Void.
- Cards usam Carbon Slate ou superfícies do DS.
- Halos e realces usam Esmeralda Soft, nunca verde sólido em grandes áreas.
- Founder Orange aparece como ponto de calor, não como superfície dominante.

---

## 8. Contraste e acessibilidade

WCAG AA é obrigatório em ambos os temas.

Princípios:

- Focus ring visível em todos os interativos.
- **Cor nunca é único indicador** — crítico em ganho/loss/bloqueio.
- Textos sobre dark usam Mist White ou equivalentes.
- Esmeralda Signal/Light são preferenciais para detalhes pequenos em dark mode.
- Em light mode, preferir Esmeralda Core/Deep para texto e bordas relevantes.

---

## 9. Checklist de aplicação

Antes de aprovar uma tela do cockpit:

1. A paleta comunica instrumento de precisão, não fintech genérica?
2. Existe separação entre cor de identidade (Esmeralda) e cor de resultado (funcional)?
3. Founder Orange aparece apenas como acento pessoal do operador?
4. O resultado é exibido **líquido** (Art. 25º)?
5. Loss/destrutivo/kill switch usam vermelho com confirmação (Arts. 18º)?
6. O layout funciona em dark mode primeiro?
7. O contraste passa WCAG AA?
8. Cor nunca é o único indicador de ganho/perda/bloqueio?
