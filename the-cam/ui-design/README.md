# Design System CAM — Hierarquia de Documentos

> Este diretório contém a especificação visual e técnica do **cockpit CaM** (The Carlos Alternative Money).
> O DS CAM serve a **uma** interface: o cockpit pessoal de operação disciplinada de mercado (WIN/WDO na B3) de Carlos.
> Não é design system de empresa, produto comercial, SaaS ou landing page — é a linguagem visual de um instrumento de operação e defesa de capital.

---

## Cadeia de Autoridade

A documentação de identidade e design segue uma hierarquia de abstração. Cada camada refina a anterior:

```
CONSTITUIÇÃO          →  Lei suprema do CaM (por quê o cockpit existe e o que ele protege)
  └── COCKPIT          →  O que é a interface (instrumento de operação e defesa de capital)
      └── BRANDING (branding-cam.md)  →  Tom visual, símbolo, linguagem (como o cockpit se apresenta)
          └── PALETA (paleta-cam.md)  →  Filosofia de cor, princípios visuais (como pensamos cor)
              └── TOKENS (tokens.md)  →  Valores atômicos — SSoT (números)
                  └── DESIGN SYSTEM   →  Componentes, padrões, regras de UI (como construímos)
                      └── LAYOUT SYSTEM →  Shells, templates, grid (como organizamos)
```

---

## Arquivos deste Diretório

| Arquivo | Responsabilidade |
|---|---|
| `branding-cam.md` | Identidade visual do cockpit — tom visual, símbolo, linguagem e padrões de marca |
| `paleta-cam.md` | Paleta Esmeralda CAM, neutros, cores funcionais e regras de uso |
| `paleta-founder.md` | Founder Orange — acento editorial pessoal de Carlos (o operador do cockpit) |
| `paleta-cam-showcase.html` | Showcase HTML puro da paleta Esmeralda CAM + Founder Orange |
| `tokens.md` | **Single Source of Truth** — cores, tipografia, espaçamento, motion, bordas, sombras, breakpoints, acessibilidade |
| `design-system.md` | Componentes, padrões de UI, stack, anti-patterns, checklist |
| `ui-library.md` | Biblioteca de UI (MUI) — tema, componentes, regras de estilização, integração |
| `analise-stack-ui-frontend.md` | Análise multi-persona sobre UI library e framework frontend do cockpit, com recomendação de stack |
| `layout-system.md` | App shell, templates de página, sidebar, grid system |
| `layout-directive.md` | Diretriz executável de layout — regras de implementação |

---

## Regra de Ouro

> **Valores atômicos (hex, rem, px, ms) existem apenas em `tokens.md`.**
> Todos os demais documentos referenciam `tokens.md` — nunca redefinem valores.

---

## Regras de defesa de capital na UI (lente Don)

O cockpit é um instrumento de preservação de capital antes de ser uma interface bonita. Toda tela operacional respeita a Constituição do CaM:

| Regra de UI | Âncora constitucional |
|---|---|
| Resultado sempre exibido **líquido** de imposto provisionado — nunca bruto | Art. 25º |
| **Kill switch** acessível, visível e acionável sem fricção | Art. 18º |
| Banner explícito de modo (**DEMO / REAL**) sempre visível em telas operacionais | Art. 19º (cobertura sistêmica) |
| Vermelho (`#EF4444`) reservado a destrutivo, loss e bloqueio — cor nunca é único indicador | `tokens.md` §1.3 |
| Verde sucesso (`#10B981`) distinto da Esmeralda institucional — sucesso ≠ marca | `paleta-cam.md` |
| Estado de bloqueio do Risk Engine comunicado de forma inequívoca | Art. 15º |

---

## Âncoras (fora de `ui-design/`)

| Documento | Localização | Relação |
|---|---|---|
| Constituição | `CONSTITUICAO.md` | Lei suprema — o que o cockpit protege |
| CLAUDE.md | `CLAUDE.md` | Contexto operacional do projeto e stack vigente |
| Stack oficial | `project/STACK-CAM-OFICIAL.md` | React 19 + Vite + MUI (frontend do cockpit) |
| SPEC do cockpit UI | `project/.../SPEC-v0.5-COCKPIT-UI` | Especificação que consome este DS |
