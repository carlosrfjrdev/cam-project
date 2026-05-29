# personas/ — INDEX (ponteiro)

> ⚠️ **O cast de personas do CaM NÃO vive mais aqui.**
>
> Por decisão arquitetural [`ADR-001 (repo-wide)`](../../project/adrs/ADR-001-perimetro-personas-cam-only.md),
> o cast foi **elevado para `/personas/` na raiz do `cam-project`** como espaço
> **CaM-only** (perímetro Art. 8º).

## Por quê

O `teczi-devflow/` tem repositório próprio e **sincroniza com a Teczilabs**.
As personas do CaM (especialmente o mundo financeiro: Mammon, Barsi, Nassim,
Jim, Wyck, Ray, Luca, Daniel) são **CaM-only e íntimas do Founder** — não podem
vazar para a Teczi via sync. Daí a separação física:

- `teczi-*` (skills, NCC-1701) → **compartilhável** com a Teczilabs.
- `/personas` + `cam-*` (skills) → **CaM-only**, fora deste diretório.

## Onde o cast vive agora

| Time | Pasta |
|---|---|
| 1 — Liderança, Gestão e Estratégia | [`/personas/1-lideranca-estrategia/`](../../personas/1-lideranca-estrategia/) |
| 2 — Tecnologia | [`/personas/2-tecnologia/`](../../personas/2-tecnologia/) |
| 3 — Governança, Segurança e Qualidade | [`/personas/3-governanca-seguranca-qa/`](../../personas/3-governanca-seguranca-qa/) |
| 4 — Experiência e Cockpit | [`/personas/4-experiencia-cockpit/`](../../personas/4-experiencia-cockpit/) |
| 5 — Financeiro, Mercado e Ativos | [`/personas/5-financeiro-mercado-ativos/`](../../personas/5-financeiro-mercado-ativos/) |
| Founder (soberano, cross-time) | [`/personas/carlos.md`](../../personas/carlos.md) |
| Aposentadas | [`/personas/_archive/`](../../personas/_archive/) |

**Mapa completo:** [`/personas/README.md`](../../personas/README.md)

> O DevFlow **referencia** o cast; não é mais **dono** dele.
