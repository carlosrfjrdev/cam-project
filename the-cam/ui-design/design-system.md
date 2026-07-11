# Design System — Cockpit CaM

> Documento consolidado e prescritivo do Design System do cockpit CaM.
> Aplicável ao frontend do cockpit (web-only — React 19 + Vite + MUI).
> Para valores atômicos (cores, tipografia, espaçamento, motion): `tokens.md` — Single Source of Truth.

---

## 1. Filosofia: "Instrumento de Precisão"

O Design System do cockpit CaM é construído para o operador disciplinado. Rejeita padrões decorativos e abraça o **brutalismo funcional**: alta densidade de informação, contraste intencional e simplicidade industrial. A interface é um instrumento de operação e defesa de capital — não uma vitrine.

### Princípios Fundamentais

- **Dark Mode First** — toda interface nasce no tema escuro e adapta para claro
- **Defesa de capital** — resultado sempre líquido (Art. 25º); kill switch acessível (Art. 18º); cor nunca é único indicador
- **Simplicidade funcional** — componentes claros, previsíveis e sem decoração desnecessária
- **Precisão Industrial** — interfaces sérias, alinhadas a grid de 4px, sem ornamentos
- **Context-Ready** — componentes semanticamente claros para manipulação por IAs (auditoras, nunca executoras — Arts. 34º-36º)
- **Densidade Controlada** — a interface suporta alta densidade sem perder legibilidade

### Personalidade Visual

- Smart, eficiente e levemente irônica
- Profundidade via **tonal layering**, não via sombras
- Separação via **espaço e variação de superfície**, não via linhas (princípio aspiracional)
- UI que parece um instrumento de precisão — sólida, autoritária e sob medida

---

## 2. Tema — Dark Mode First

O cockpit CaM adota **Dark Mode como tema padrão** (sessões longas de tela).

### Hierarquia de Superfícies

> Tabelas completas de superfícies (dark + light) e tokens semânticos: `tokens.md` (seções 2 e 2.3)

Cinco camadas de profundidade — background → surface-1 → surface-2 → surface-3 → elevated — criam hierarquia visual sem sombras.

### Regras de Tema

- O tema padrão é **escuro** — toggle permite mudar para claro
- Persistir preferência do usuário; fallback para `prefers-color-scheme`
- Em dark mode: bordas sutis (`branco 10–15%`) para separar superfícies; sombras ineficazes — preferir bordas e variação de superfície
- Em light mode: ghost borders (15% opacity) quando necessário para WCAG AA
- Textos sobre fundo escuro: branco 100% (títulos), 90% (subtítulos), 70–80% (parágrafos)
- Esmeralda CAM é a identidade do cockpit; cor de resultado é funcional; Founder Orange é acento do operador
- Evitar #000000 absoluto (causa "smearing" em OLED) — usar deep charcoals

---

## 3. Tipografia

### Fontes e Escala Tipográfica

> Tabela completa de fontes, escala de 8 tamanhos e responsividade: `tokens.md` (seção 3)

Par tipográfico: **Poppins** (headings, semibold 600) + **Inter** (body, regular 400). Identidade "Tech-Editorial": Poppins oferece personalidade geométrica e bold; Inter garante legibilidade em densidade de dados.

### Regras Tipográficas

- Headings com `tracking-tight` (letter-spacing compacto)
- Labels em `uppercase` com `tracking-wider` para metadados de sistema
- Body text nunca abaixo de 12px
- Em páginas de aplicação, títulos usam tamanho fixo (`text-2xl` para h1) — sem `clamp()`
- `clamp()` reservado apenas para landing pages e hero sections

---

## 4. Stack do Cockpit (web-only)

### 4.1 Web — React 19 + Vite

> Stack oficial: `../../project/STACK-CAM-OFICIAL.md`. O cockpit é uma SPA local, sem Next.js e sem frontend mobile nativo.

| Camada | Tecnologia |
|---|---|
| Framework | React 19 + Vite (SPA local) |
| UI Library | MUI (@mui/material) |
| Ícones | @mui/icons-material (Outlined padrão) |
| Estilização | MUI System (sx prop + styled()) + Emotion |
| Formulários | React Hook Form + Zod |
| Estado servidor | React Query (@tanstack/react-query) |
| Estado UI | Zustand |

#### Regras Web

- Tokens do Design System mapeados via `createTheme()` do MUI
- Detalhes completos de configuração do tema: [`ui-library.md`](ui-library.md) e [`mui-theme-cam.md`](mui-theme-cam.md)
- MUI como camada de componentes — customizar via tema, não override direto
- `sx` prop para overrides pontuais (1–3 props)
- `styled()` para componentes reutilizados em 3+ lugares
- 1 componente por arquivo
- Imports absolutos com `@/`
- Sem `any` — usar `unknown` quando tipo incerto
- React Query para data fetching — nunca `useEffect + fetch`
- Não usar `style={{...}}` inline — apenas `sx` ou `styled()`
- Não usar TailwindCSS, CSS Modules ou Styled Components
- Proibido hex solto no `sx` — usar `theme.palette` ou tokens semânticos

---

## 5. Elevação e Profundidade: Tonal Layering

Não usamos drop shadows tradicionais. Usamos **luz ambiente** e **variação tonal**.

### Princípio de Layering

Profundidade é "construída", não "projetada". Um card não precisa de sombra se estiver em `surface-1` sobre um background `#1A1A1A`. A variação de cor é a fronteira.

### Ghost Border

Quando uma fronteira é necessária para WCAG AA (especialmente em light mode), usar `border` com opacidade de **10-15%**. Deve parecer uma sugestão de borda, não uma restrição física.

### Regras

| Contexto | Dark Mode | Light Mode |
|---|---|---|
| Cards | Sem sombra, tonal shift (`surface-1` sobre `background`) | `shadow-sm` opcional |
| Modais | Sombra tinted: `0px 20px 40px rgba(0,0,0,0.4)` | `shadow-lg` |
| Floating (tooltips) | `surface-2` com `backdrop-blur-md` e `opacity-90` | `shadow-md` |
| Sidebar | Um step mais escuro/claro que o content area | Idem |

---

## 6. Componentes Compartilhados

### 6.1 Botões

| Propriedade | Valor |
|---|---|
| Border radius | 4px (`rounded-md`) |
| Transição | ~200ms (ease) |
| Focus | Ring 2px na cor primária |
| Active | Escala 98% |

| Variante | Fundo | Texto | Borda |
|---|---|---|---|
| Primary | `#059669` | Branco | — |
| Secondary | `--secondary` | `--foreground` | — |
| Outline | Transparente | `#059669` | `#059669` |
| Ghost | Transparente | `--foreground` | — |
| Destructive | `#EF4444` | Branco | — |

- Não usar `rounded-full` (pills) — pills são "amigáveis demais"; preferimos "prático"
- Não usar `rounded-none` (cantos vivos)

### 6.2 Inputs

| Propriedade | Dark | Light |
|---|---|---|
| Fundo | `--secondary` (`#2C2C2C`) | `--secondary` (`#F0F0F0`) |
| Borda | `border` token (10% opacity) | `border` token |
| Borda focus | `--primary` | `--primary` |
| Border radius | 4px | 4px |
| Focus | Ring 2px na cor primária | Ring 2px na cor primária |

- Label visível obrigatório — nunca remover

### 6.3 Cards

| Propriedade | Dark | Light |
|---|---|---|
| Fundo | `--card` (`#1F1F1F`) | `--card` (`#FFFFFF`) |
| Borda | `rgba(255,255,255,0.08)` | `#E5E5E5` |
| Borda hover | `rgba(5,150,105,0.4)` | `rgba(5,150,105,0.4)` |
| Border radius | 6px (`rounded-lg`) | 6px |
| Padding | 24px | 24px |

- Sem divider lines entre list items dentro de cards — usar gap e hover state

### 6.4 Badges / Pills

| Tipo | Fundo | Texto |
|---|---|---|
| Default | `--primary` 15% | `--primary` |
| Success | `--success` 15% | `--success` |
| Warning | `--warning` 15% | `--warning` |
| Error | `--destructive` 15% | `--destructive` |
| Info | `--info` 15% | `--info` |

### 6.5 Navegação

- **Header**: Full-width, `bg-background`, `border-b`, com banner de modo DEMO/REAL e acesso ao kill switch
- **Sidebar**: `bg-sidebar` (token), hover em `bg-sidebar-accent`

---

## 7. Iconografia

| Biblioteca | Plataforma |
|---|---|
| @mui/icons-material | Web (React 19 + Vite) |

- Variante padrão: **Outlined** (stroke) — alinhado com a estética minimalista do cockpit
- Variante **Filled** apenas em ícones de navegação ativa
- Símbolo da marca: mira / crosshair (ver `branding-cam.md`)
- Imports nomeados obrigatórios para tree-shaking: `import { HomeOutlined } from '@mui/icons-material'`

| Tamanho | Uso |
|---|---|
| 16px (`size-4`) | Inline em textos, badges |
| 20px (`size-5`) | Botões, inputs, nav items |
| 24px (`size-6`) | Navegação, listas |
| 32px+ (`size-8+`) | Feature cards, hero sections |

---

## 8. Motion / Animações

> Tabela de durações, easings e biblioteca: `tokens.md` (seção 5)

### Princípios

- Suave sempre — sem animações bruscas
- Funcional — comunica mudança de estado, não decora
- Rápida — o usuário nunca "espera" animação terminar
- Preferir `transform` e `opacity` (GPU-accelerated)

---

## 9. Espaçamento (Escala 4px)

> Tabela completa de tokens de espaçamento: `tokens.md` (seção 4)

### Regra

- Grid de **4px obrigatório**: se um espaçamento é 7px, está errado — arredondar para 8px
- Valores arbitrários fora da escala são proibidos

---

## 10. Acessibilidade

- **WCAG AA obrigatório** em ambos os temas
- Focus ring visível (2px, cor primária) em todos os elementos interativos — **nunca remover**
- Contraste mínimo 4.5:1 para textos, 3:1 para elementos gráficos
- Cores funcionais nunca como único indicador — usar ícone + texto
- Labels obrigatórios em inputs (visíveis ou `aria-label`)
- Touch target mínimo: 44x44px (mobile)
- Body text nunca abaixo de 12px
- Navegação por teclado com ordem lógica de `tabindex`

---

## 11. Anti-patterns (Proibido)

| Anti-pattern | Correção |
|---|---|
| `#000000` ou `#FFFFFF` absoluto | Usar tokens de superfície |
| `rounded-full` (pills) em botões | Usar `borderRadius: 4` (MUI) |
| Drop shadows em dark mode | Usar bordas sutis e tonal shift |
| Cores hexadecimais soltas no código | Usar `theme.palette` ou tokens semânticos |
| `style={{...}}` inline | Usar `sx` prop ou `styled()` |
| TailwindCSS, CSS Modules | Usar MUI System |
| shadcn/ui, Radix UI | Usar MUI (@mui/material) |
| Lucide React | Usar @mui/icons-material |
| Componentes > 150 linhas | Extrair sub-componentes |
| `useEffect + fetch` | Usar React Query |
| `any` em TypeScript | Usar `unknown` |
| Espaçamentos fora da escala 4px | Usar tokens de espaçamento |

---

## 12. Checklist de Padronização (IA/Review)

1. [ ] Usa `Poppins` em títulos? (Obrigatório h1-h4)
2. [ ] Usa tokens semânticos de cor? (Nunca hex solto)
3. [ ] Ações destrutivas em vermelho (`destructive`)?
4. [ ] Focus ring visível em todos os interativos?
5. [ ] `aria-label` em botões apenas com ícone?
6. [ ] Contraste WCAG AA em ambos os temas?
7. [ ] Espaçamentos na escala de 4px?
8. [ ] Sem sombras em dark mode? (Bordas sutis)
9. [ ] `body-md` (14px) ou `body` (16px) como padrão de texto?
10. [ ] Inputs com label visível?
11. [ ] Usa MUI como biblioteca de componentes? (Não shadcn/ui)
12. [ ] Ícones via @mui/icons-material? (Não Lucide React)
13. [ ] Estilização via sx prop ou styled()? (Não TailwindCSS)
14. [ ] Resultado exibido **líquido** de imposto provisionado? (Art. 25º)
15. [ ] Kill switch acessível e em vermelho destrutivo? (Art. 18º)
16. [ ] Banner de modo DEMO/REAL visível em telas operacionais? (Art. 19º)
17. [ ] Cor nunca é único indicador de ganho/loss/bloqueio?

---

## 13. Referências

| Documento | Descrição |
|---|---|
| `paleta-cam.md` | Cores, tipografia e contraste detalhados |
| `branding-cam.md` | Identidade visual e padrões de componentes |
| `../../CONSTITUICAO.md` | Lei suprema — o que o cockpit protege |
| `../../project/STACK-CAM-OFICIAL.md` | Stack oficial do cockpit |
| `ui-library.md` | Biblioteca de UI (MUI) — tema, componentes, regras |
| `mui-theme-cam.md` | Especificação do tema MUI do cockpit |
| `layout-system.md` | Primitivos de layout, shells e templates |
| `layout-directive.md` | Diretriz operacional de layout |
