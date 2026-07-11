# Design Tokens — Cockpit CaM

> **Single Source of Truth** para todos os valores atômicos do Design System CAM.
> Versão: 1.0 | Abordagem: Dark Mode First

**Hierarquia:** `CONSTITUIÇÃO` → `cockpit` → `branding` → **`tokens`** → `design-system` → `layout-system`

> Nenhum outro documento deve redefinir valores presentes aqui. Documentos de nível superior (`branding`, `paleta`) descrevem **filosofia de uso** — este documento define **valores canônicos**.

---

## 1. Cores

### 1.1 Primárias (Esmeralda CAM)

| Nome | Token | Hex | RGB | Uso |
|---|---|---|---|---|
| Esmeralda CAM | `--primary` | `#059669` | `rgb(5, 150, 105)` | Cor principal de identidade do cockpit, CTAs, links de ação, acento estratégico |
| Esmeralda Core | `--primary-dark` | `#047857` | `rgb(4, 120, 87)` | Hover/pressed states, CTAs ativos, texto em light mode |
| Esmeralda Light | `--primary-light` | `#34D399` | `rgb(52, 211, 153)` | Highlights, badges, foco e acentos em dark mode |
| Esmeralda Void | `--primary-deep` | `#061711` | `rgb(6, 23, 17)` | Fundos institucionais profundos |
| Esmeralda Soft | `--primary-soft` | `rgba(5,150,105,0.14)` | — | Fundos tonais, badges e halos |

> **Regra:** Esmeralda CAM é identidade do cockpit, não cor de resultado. Ganho/loss usam as cores funcionais (§1.3). Máximo 1 CTA primário por seção. Proibido em textos longos.

### 1.2 Neutras

| Nome | Token | Hex | RGB | Uso |
|---|---|---|---|---|
| Soft White | `--neutral-50` | `#F7F7F7` | `rgb(247, 247, 247)` | Background principal (light theme) |
| Branco Puro | `--neutral-0` | `#FFFFFF` | `rgb(255, 255, 255)` | Cards elevados, modais, inputs, overlays |
| Cinza Claro | `--neutral-200` | `#D9D9D9` | `rgb(217, 217, 217)` | Bordas, separadores, fundos sutis |
| Cinza Médio | `--neutral-500` | `#4A4A4A` | `rgb(74, 74, 74)` | Parágrafos, textos secundários |
| Gray BG | `--neutral-800` | `#2C2C2C` | `rgb(44, 44, 44)` | Seções escuras alternadas, blocos de código |
| Cinza Chumbo | `--neutral-850` | `#1F1F1F` | `rgb(31, 31, 31)` | Títulos escuros, cards dark |
| Dark BG | `--neutral-900` | `#1A1A1A` | `rgb(26, 26, 26)` | Background principal (dark theme), heroes, footers |

### 1.3 Funcionais

| Nome | Token | Hex | RGB | Uso |
|---|---|---|---|---|
| Azul Inteligência | `--info` | `#0EA5E9` | `rgb(14, 165, 233)` | Saídas de IA (auditora/analista, nunca executora — Arts. 34º-36º), badges de sistema |
| Verde Confirmação | `--success` | `#10B981` | `rgb(16, 185, 129)` | Sucesso, ganho líquido, confirmações, badges positivos |
| Vermelho Alerta | `--destructive` | `#EF4444` | `rgb(239, 68, 68)` | Loss, ações destrutivas, kill switch (Art. 18º), bloqueio do Risk Engine (Art. 15º) |
| Amarelo Atenção | `--warning` | `#F59E0B` | `rgb(245, 158, 11)` | Avisos, DARF pendente (Art. 26º), modo demo, limite próximo |

> **Defesa de capital (lente Don):** estas cores carregam significado operacional crítico. Resultado é sempre exibido **líquido** de imposto provisionado (Art. 25º). **Cor nunca é único indicador** — ganho/loss/bloqueio sempre acompanham ícone + texto.

### 1.4 Extras (Acentos de Marca)

| Nome | Token | Hex | RGB | Uso |
|---|---|---|---|---|
| Roxo Epic | `--accent-purple` | `#8B5CF6` | `rgb(139, 92, 246)` | Issues do tipo Epic, hierarquia de alto nível |
| Rosa Magenta | `--accent-pink` | `#EC4899` | `rgb(236, 72, 153)` | Complementa roxo/esmeralda, energia tech |
| Teal Profundo | `--accent-teal` | `#0D9488` | `rgb(13, 148, 136)` | Complementa verde/azul, estabilidade |
| Founder Orange | `--founder-orange` | `#FF7A00` | `rgb(255, 122, 0)` | Acento editorial do Founder, origem e faísca criativa |
| Founder Ember | `--founder-ember` | `#C2410C` | `rgb(194, 65, 12)` | Versão profunda do Founder Orange |
| Founder Glow | `--founder-glow` | `#FDBA74` | `rgb(253, 186, 116)` | Brilho pontual e microdetalhes |

---

## 2. Superfícies (Surface Hierarchy)

### 2.1 Dark Theme (Padrão)

| Token | Hex | RGB | Uso |
|---|---|---|---|
| `--background` | `#1A1A1A` | `rgb(26, 26, 26)` | Fundo principal da aplicação |
| `--surface-1` | `#1F1F1F` | `rgb(31, 31, 31)` | Cards, painéis laterais, sidebar |
| `--surface-2` | `#2C2C2C` | `rgb(44, 44, 44)` | Inputs, dropdowns, áreas interativas |
| `--surface-3` | `#3A3A3A` | `rgb(58, 58, 58)` | Hover states de superfícies |
| `--elevated` | `#444444` | `rgb(68, 68, 68)` | Modais, popovers, tooltips |

### 2.2 Light Theme

| Token | Hex | RGB | Uso |
|---|---|---|---|
| `--background` | `#F7F7F7` | `rgb(247, 247, 247)` | Fundo principal da aplicação |
| `--surface-1` | `#FFFFFF` | `rgb(255, 255, 255)` | Cards, painéis laterais, sidebar |
| `--surface-2` | `#F0F0F0` | `rgb(240, 240, 240)` | Inputs, dropdowns, áreas interativas |
| `--surface-3` | `#E5E5E5` | `rgb(229, 229, 229)` | Hover states de superfícies |
| `--elevated` | `#FFFFFF` | `rgb(255, 255, 255)` | Modais, popovers, tooltips (com sombra) |

### 2.3 Tokens Semânticos (Theme-Agnostic)

| Token | Dark | Light | Uso |
|---|---|---|---|
| `--primary` | `#059669` | `#047857` | Cor primária institucional |
| `--primary-foreground` | `#FFFFFF` | `#FFFFFF` | Texto sobre primária |
| `--secondary` | `#2C2C2C` | `#F0F0F0` | Cor secundária |
| `--muted` | `#2C2C2C` | `#F0F0F0` | Cor muted |
| `--muted-foreground` | `#A0A0A0` | `#4A4A4A` | Texto muted |
| `--foreground` | `#FFFFFF` | `#1F1F1F` | Texto padrão |
| `--card` | `#1F1F1F` | `#FFFFFF` | Background de cards |
| `--card-foreground` | `#FFFFFF` | `#1F1F1F` | Texto em cards |
| `--border` | `rgba(255,255,255,0.10)` | `#D9D9D9` | Bordas padrão |
| `--input` | `#2C2C2C` | `#F0F0F0` | Background de inputs |
| `--ring` | `#10B981` | `#059669` | Focus ring |
| `--destructive` | `#EF4444` | `#EF4444` | Ações destrutivas |
| `--success` | `#10B981` | `#10B981` | Status sucesso |
| `--warning` | `#F59E0B` | `#F59E0B` | Status warning |
| `--info` | `#0EA5E9` | `#0EA5E9` | Status informação |

---

## 3. Tipografia

### 3.1 Fontes

| Contexto | Fonte | Weight | CSS Weight |
|---|---|---|---|
| Headings (h1–h6) | Poppins | Semibold | 600 |
| Body (p, span, li) | Inter | Regular | 400 |

### 3.2 Escala Tipográfica (8 tamanhos)

| Token | Elemento | Tamanho | Rem | Line Height | Fonte/Weight |
|---|---|---|---|---|---|
| `--text-display` | Display / Hero | 48px | 3rem | 1.1 | Poppins 600 |
| `--text-h1` | h1 | 42px | 2.625rem | 1.2 | Poppins 600 |
| `--text-h2` | h2 | 32px | 2rem | 1.2 | Poppins 600 |
| `--text-h3` | h3 | 24px | 1.5rem | 1.3 | Poppins 600 |
| `--text-body` | Body | 16px | 1rem | 1.6 | Inter 400 |
| `--text-dense` | Body Dense | 14px | 0.875rem | 1.4 | Inter 400 |
| `--text-small` | Small | 13px | 0.8125rem | 1.4 | Inter 400 |
| `--text-caption` | Caption | 12px | 0.75rem | 1.4 | Inter 400 |

> **Mínimo absoluto:** 12px — nunca abaixo, em nenhum contexto.

### 3.3 Responsividade — Full Web (desktop-first)

O CaM é **aplicação de gestão financeira local** — **full web, desktop-first**. NÃO é mobile-first.
As telas **podem ser visualizadas em celular** (responsivo para leitura), mas a **interação/operação
mobile se dá via Robô Telegram** (spec futura), nunca pela UI web no celular. Layout otimizado para
desktop (tela de gestão). Breakpoints abaixo definem a degradação responsiva para visualização:

| Token | Mobile (< 768px) | Tablet (≥ 768px) | Desktop (≥ 1024px) |
|---|---|---|---|
| `--text-display` | 32px | 40px | 48px |
| `--text-h1` | 28px | 36px | 42px |
| `--text-h2` | 24px | 28px | 32px |
| `--text-h3` | 20px | 22px | 24px |
| `--text-body` | 16px | 16px | 16px |
| `--text-dense` | 14px | 14px | 14px |
| `--text-small` | 13px | 13px | 13px |
| `--text-caption` | 12px | 12px | 12px |

> **Telas de identidade e painéis de destaque** podem usar `clamp()` para fluidez adicional:
> - h1: `clamp(2rem, 5vw, 3.5rem)`
> - h2: `clamp(1.75rem, 4vw, 2.5rem)`
> - h3: `clamp(1.25rem, 3vw, 1.75rem)`

### 3.4 Plataforma

O cockpit CaM é **web-only**: React 19 + Vite + MUI (ver `../../project/STACK-CAM-OFICIAL.md`). Não há frontend mobile nativo. Os tokens tipográficos mapeiam diretamente para o tema MUI (`createTheme`) — ver `mui-theme-cam.md`.

### 3.5 Texto em Dark Mode

| Elemento | Cor | Opacidade |
|---|---|---|
| Títulos | `#FFFFFF` | 100% |
| Subtítulos | `rgba(255,255,255,0.90)` | 90% |
| Parágrafos | `rgba(255,255,255,0.70-0.80)` | 70–80% |
| Destaques/Acentos | `#34D399` | 100% |
| Links | `#34D399`, hover `#10B981` | 100% |

> **Regra:** Nunca usar cinza escuro sobre fundo escuro — contraste insuficiente.

---

## 4. Espaçamento

### 4.1 Escala (Grid de 4px — Obrigatório)

| Token | Valor | Rem | Uso |
|---|---|---|---|
| `space-1` | 4px | 0.25rem | Micro espaçamentos |
| `space-2` | 8px | 0.5rem | Entre ícone e texto, dentro de grupos |
| `space-3` | 12px | 0.75rem | Padding interno compacto |
| `space-4` | 16px | 1rem | Gap padrão entre elementos |
| `space-6` | 24px | 1.5rem | Padding de cards, entre seções |
| `space-8` | 32px | 2rem | Separação entre blocos |
| `space-12` | 48px | 3rem | Padding vertical adicional |
| `space-16` | 64px | 4rem | Separação entre seções |
| `space-24` | 96px | 6rem | Padding vertical de hero sections |

> **Regra crítica:** Grid de 4px obrigatório. Valores arbitrários fora da escala são **PROIBIDOS**. Se um espaçamento é 7px, arredondar para 8px.

### 4.2 Regras por Contexto

| Contexto | Padrão |
|---|---|
| Padding interno de cards | 24–32px (`space-6` a `space-8`) |
| Padding vertical de seções | 64–96px (`space-16` a `space-24`) |
| Gaps entre elementos | 16px, 24px ou 32px |

---

## 5. Motion & Animações

### 5.1 Biblioteca

**Tailwind Animate** (preferencial). Pode ser expandido com outra biblioteca por demanda específica.

### 5.2 Durações

| Token | Duração | Easing | Uso |
|---|---|---|---|
| `--duration-fast` | 150ms | `ease` | Hover transitions, fechamento |
| `--duration-default` | 200ms | `ease` | Transições padrão |
| `--duration-slow` | 250ms | `ease` | Abertura de modais, drawers |

### 5.3 Princípios

- **Suave** — sem animações bruscas
- **Funcional** — comunica mudança de estado, não decora
- **Rápida** — o usuário nunca "espera" animação terminar
- Preferir `transform` e `opacity` (GPU-accelerated)

---

## 6. Bordas & Raio

### 6.1 Border Radius

| Contexto | Tamanho | Tailwind Class |
|---|---|---|
| Botões | 4px | `rounded-md` |
| Cards | 6px | `rounded-lg` |
| Inputs | 4px | `rounded-md` |

> **Proibições:** `rounded-full` (pills — "amigáveis demais") e `rounded-none` (cantos vivos).

### 6.2 Bordas por Contexto

| Contexto | Dark | Light |
|---|---|---|
| Card | `rgba(255,255,255,0.08)` | `#E5E5E5` |
| Card hover | `rgba(5,150,105,0.4)` | `rgba(5,150,105,0.4)` |
| Ghost (WCAG AA) | `rgba(255,255,255,0.10-0.15)` | calculado |
| Input | token 10% opacity | token 100% |
| Input focus | `#10B981` | `#059669` |
| Padrão (`--border`) | `rgba(255,255,255,0.10)` | `#D9D9D9` |

### 6.3 Focus Ring (Acessibilidade)

| Propriedade | Valor |
|---|---|
| Largura | 2px |
| Cor | `--ring` (`#10B981` dark / `#059669` light) |
| Obrigatório | SIM — nunca remover |

---

## 7. Sombras & Elevação

### 7.1 Abordagem

Dark mode **não usa drop shadows tradicionais**. Usa **tonal layering** (variação de cor) + **bordas sutis**.

| Contexto | Dark Mode | Light Mode |
|---|---|---|
| Cards | Sem sombra (tonal shift) | `shadow-sm` (opcional) |
| Modals | `0px 20px 40px rgba(0,0,0,0.4)` | `shadow-lg` |
| Floating (tooltips) | `surface-2` + `backdrop-blur-md` + opacity 90% | `shadow-md` |

> **Princípio:** Profundidade é "construída" (layering), não "projetada" (shadow). Um card em `surface-1` sobre `background` já tem profundidade visual.

---

## 8. Breakpoints

| Nome | Tamanho | Tailwind Prefix | Uso |
|---|---|---|---|
| Mobile | < 768px | (default) | 1 coluna — só **visualização** (interação via Robô Telegram) |
| Tablet | ≥ 768px | `md:` | 2 colunas |
| Desktop | ≥ 1024px | `lg:` | 3+ colunas |
| Wide | ≥ 1280px | `xl:` | Layouts expandidos |

> **Touch target mínimo:** 44x44px em mobile (acessibilidade tátil).

---

## 9. Acessibilidade (WCAG AA)

### 9.1 Contrastes Testados

| Combinação | Contraste | Status |
|---|---|---|
| `#047857` sobre `#FFFFFF` | 5.5:1 | AA |
| `#FFFFFF` sobre `#1A1A1A` | 18.5:1 | AAA |
| `rgba(255,255,255,0.80)` sobre `#1A1A1A` | 14.8:1 | AAA |
| `#F7F7F7` sobre `#1A1A1A` | 16.8:1 | AAA |
| `#4A4A4A` sobre `#F7F7F7` | 6.9:1 | AA |
| `#34D399` sobre `#1A1A1A` | 9.4:1 | AAA |

### 9.2 Requisitos Obrigatórios

| Requisito | Padrão |
|---|---|
| Conformidade | WCAG AA (mínimo) |
| Focus ring visível | 2px, `--ring` — nunca remover |
| Contraste para textos | ≥ 4.5:1 |
| Contraste para elementos gráficos | ≥ 3:1 |
| Labels em inputs | Visível ou `aria-label` |
| Touch target mobile | ≥ 44x44px |
| Body text mínimo | 12px |
| Cor como único indicador | Proibido |
| Navegação por teclado | Ordem lógica de tabindex |

---

## 10. Iconografia

| Tamanho | Px | Tailwind Class | Uso |
|---|---|---|---|
| Extra small | 16px | `size-4` | Inline em textos, badges |
| Small | 20px | `size-5` | Botões, inputs, nav items |
| Standard | 24px | `size-6` | Navegação, listas |
| Large | 32px+ | `size-8+` | Feature cards, hero sections |

**Estilo:** Variante **Outlined** como padrão web (@mui/icons-material), **Filled** apenas em nav item ativo.
**Biblioteca:** @mui/icons-material.

---

## 11. Regras Globais

| Regra | Descrição |
|---|---|
| **Dark Mode First** | Tema padrão: escuro. Persistir preferência; fallback `prefers-color-scheme` |
| **Grid de 4px** | Todos os espaçamentos na escala de 4px. Valores arbitrários proibidos |
| **WCAG AA** | Obrigatório em ambos os temas |
| **No Drop Shadows (Dark)** | Usar tonal layering + bordas sutis |
| **Esmeralda = Identidade** | Identidade do cockpit; cor de resultado é funcional; max 1 CTA primário por seção |
| **Founder Orange = Spark** | Acento editorial/pessoal do operador; nunca dominante |
| **Líquido sempre** | Resultado exibido líquido de imposto provisionado (Art. 25º) — nunca bruto |
| **Cor ≠ único indicador** | Ganho/loss/bloqueio sempre com ícone + texto |
| **MUI como UI Library** | Obrigatório no frontend do cockpit |
| **@mui/icons-material** | Ícones via import nomeado, variante Outlined padrão |
| **12px Mínimo** | Nenhum texto abaixo de 12px |

---

## Referências

| Documento | Relação |
|---|---|
| `../../CONSTITUICAO.md` | Lei suprema — o que o cockpit protege (upstream) |
| `branding-cam.md` | Princípios visuais e identidade do cockpit (upstream) |
| `paleta-cam.md` | Filosofia de cor (upstream) |
| `paleta-founder.md` | Founder Orange — acento do operador (upstream) |
| `design-system.md` | Componentes e padrões (downstream) |
| `layout-system.md` | Shells e templates (downstream) |
| `layout-directive.md` | Diretriz de layout (downstream) |
