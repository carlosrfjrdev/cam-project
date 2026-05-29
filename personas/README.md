# personas/ — Cast do CaM em 5 Times

> **Cast CaM-only.** Espaço de primeira classe na raiz do `cam-project`
> ([`ADR-001 repo-wide`](../project/adrs/ADR-001-perimetro-personas-cam-only.md)) —
> **não** vive mais em `teczi-devflow/` para não vazar para a Teczilabs (Art. 8º).
>
> `teczi-*` é compartilhável; **`/personas` e `cam-*` são CaM-only.**

---

## O Founder

| | |
|---|---|
| 👨‍💻 **Carlos** | [`carlos.md`](carlos.md) — Founder, soberano constitucional (Art. 43º). **Cross-time, fora dos 5 times.** Guardião do perímetro; não é membro de nenhum time (D6). |

> O Founder é o **volante**. Mammon é o **acelerador**. O Risk Engine é o **freio**.

---

## Os 5 Times

### Time 1 — Liderança, Gestão e Estratégia · [`1-lideranca-estrategia/`](1-lideranca-estrategia/)
| Persona | Papel | Cor | Ícone |
|---|---|---|---|
| leo | Orquestrador-chefe (ponto único de entrada; **bi-mundo**) | `#E65100` Deep Orange | Crown |
| marty | Discovery / In-Out-Later | `#1A237E` Deep Indigo | Telescope |
| albert | Especificação / SPEC | `#F59E0B` Amber | Lightbulb |
| nico | Planejamento / PLAN | `#8B5CF6` Purple | ClipboardList |
| peter | Produto & Valor (outcome = **capital preservado + patrimônio**) | `#3B82F6` Blue | Target |
| voltaire | Devil's advocate / challenger | `#881337` Wine | Sword |
| sun | **Estrategista híbrido tech+mercado** (postura cross-mundo) | `#6366F1` Indigo | Compass |

### Time 2 — Tecnologia · [`2-tecnologia/`](2-tecnologia/)
| Persona | Papel | Cor | Ícone |
|---|---|---|---|
| oscar | Arquitetura / ADR / DAS | `#0EA5E9` Blue | Building2 |
| nikola | Desenvolvimento / CODE | `#10B981` Green | Code2 |
| tom | Versionamento / Git / GitHub | `#334155` Slate Deep | GitBranch |
| vint | Infra / Cloud / OPS / DEPLOY exec | `#64748B` Slate | Server |
| ada | Dados / banco / modelagem | `#F43F5E` Rose | Database |
| grace | Arquitetura de tecnologia / stack | `#EAB308` Gold | Blocks |
| alan | IA & inteligência agêntica | `#22D3EE` Cyan | Cpu |
| steve | Release / narrativa de entrega | `#EC4899` Pink | Rocket |

### Time 3 — Governança, Segurança e Qualidade · [`3-governanca-seguranca-qa/`](3-governanca-seguranca-qa/)
| Persona | Papel | Cor | Ícone |
|---|---|---|---|
| kevin | InfoSec **+ guardião técnico constitucional** | `#166534` Forest Green | Fingerprint |
| linus | QA (QA-CR + QA-Func + QA-SEC) | `#0D9488` Teal | ShieldCheck |
| bill | Estado BUG — RCA de defeito | `#EF4444` Red | Bug |
| denis | Conhecimento / documentação / SDOC | `#84CC16` Lime | BookOpen |
| howard | Arqueologia de software / DRIFT | `#A67C52` Sandy Brown | ScanSearch |

### Time 4 — Experiência e Cockpit · [`4-experiencia-cockpit/`](4-experiencia-cockpit/)
| Persona | Papel | Cor | Ícone |
|---|---|---|---|
| don | **UX como defesa de capital** (líquido Art. 25º, kill switch Art. 18º) | `#F97316` Orange | Users |
| andy | Design visual / identidade / cockpit | `#D946EF` Fuchsia | Palette |

### Time 5 — Financeiro, Mercado e Ativos · [`5-financeiro-mercado-ativos/`](5-financeiro-mercado-ativos/)
| Persona | Papel | Mundo | Cor | Ícone | Símbolo |
|---|---|---|---|---|---|
| **mammon** | Vetor ofensivo da prosperidade (**read-only Art. 35º**) | financeiro + assento Time 1 | `#D4AF37` Gold | Star | ⭐ |
| **ray** | Macro / ciclos / regime de mercado | mercado | `#0E7490` Petróleo | Globe | 🌐 |
| **jim** | Quant / edge / Evidence Pack | mercado | `#7E22CE` Violeta Quant | FlaskConical | 🧪 |
| **wyck** | Fluxo / tape / book L2 / microestrutura | mercado | `#B45309` Bronze | CandlestickChart | 🕯️ |
| **nassim** | Risco de ruína / tail / sizing | risco | `#7F1D1D` Carmim Escuro | TrendingDown | 🦢 |
| **barsi** | Carteira Hard / dividendos / FIIs / R-20 | ativos / patrimônio | `#065F46` Verde Perene | TreePine | 🌳 |
| **luca** | Fiscal / ledger / provisão / journal duplo | fiscal | `#1E3A8A` Azul Ledger | BookOpenCheck | 📒 |
| **daniel** | RCA do operador / vieses / decisão | decisão | `#27272A` Grafite | Brain | 🧠 |
| fred | Analista de domínio do **mercado** (vocabulário ubíquo) | domínio | `#78716C` Stone | Workflow | — |

---

## Aposentadas · [`_archive/`](_archive/)

| Persona | Status | Substituída por |
|---|---|---|
| florence | aposentada 2026-05-28 (D4) | don (UX como defesa de capital) |

---

## Regras de cast (invariantes)

1. **Cor exclusiva** — cada persona tem um hex único (inventário acima; sem colisão).
2. **Código estável** — `MAIÚSCULO`, nunca muda (ex.: `MAMMON`, `NASSIM`).
3. **Mundo declarado** — toda persona financeira declara *mundo* + *ancoragem constitucional* + *fronteira* (com quem não se confunde).
4. **Trava read-only (Art. 35º)** — personas financeiras **propõem**, nunca executam ordem nem justificam exceção constitucional. Mammon é o caso emblemático.
5. **Bi-mundo só por design** — apenas **Leo** (orquestração) e **Sun** (postura) cruzam tech↔mercado. Mammon tem assento no Time 1 mas mundo-proa é financeiro.
6. **Founder soberano** — Carlos é guardião constitucional cross-time; NÃO existe persona de compliance (D6).
7. **Perímetro** — este diretório é **CaM-only** (Art. 8º). Nada aqui sincroniza com a Teczilabs.

---

## Hierarquia que todo o cast serve

```
Constituição > Risk Engine > Estratégia validada > IA > Operador em decisão manual
```

Nenhuma persona — nem Mammon — sobrevive fora dessa hierarquia.

---

## Catálogos legados

`personas-teczilabs.md` e `personas-devflow.md` (raiz deste diretório) são
catálogos herdados da fase Teczilabs, preservados como referência histórica.
**Este README é a fonte autoritativa do cast do CaM.**
