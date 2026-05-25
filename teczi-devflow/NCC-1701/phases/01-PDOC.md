# Fase 01 — PDOC (Project Documentation Setup)

> **Codinome:** NCC-1701 · **Status:** Draft
> **Lead:** Leo + Denis
> **Decisão herdada:** SCOPE-FINAL §6.1 (ordem 1)

## 1. Propósito

Registrar um projeto, organizar sua estrutura de pastas/repos e estabelecer o contexto inicial mínimo para que as fases seguintes encontrem terreno.

## 2. Quando rodar

- **Sempre que nasce um projeto novo** (produto, módulo standalone ou frente cross-produto).
- **Skip** quando o projeto já existe e está documentado.

Aplicação por P/M/G (ver `process.md` §5):

| P | M | G |
|---|---|---|
| Skip se projeto existe | Condicional | Recomendado se novo produto/frente |

## 3. Entradas

| Artefato | Origem | Obrigatório |
|---|---|---|
| Intenção do Founder (verbal/textual) | Founder | sim |
| Codinome proposto | Founder | sim |
| Domínio inicial (produto/cliente/contexto) | Founder | sim |

## 4. Saídas

| Artefato | Template | Persistência (Stage 0) |
|---|---|---|
| Estrutura de pastas do projeto | — | Repositório do produto |
| README inicial | — | Raiz do projeto |
| Vínculo com `teczilabs/produtos/{produto}/` quando aplicável | — | Workspace ecosystem |
| Notas iniciais de contexto | — | `/projects/{produto}/notes/` |

## 5. Personas

- **Lead:** Leo (orquestração) + Denis (documentação)
- **Co-lead:** —
- **Cross-cutting:** —

## 6. Gate de saída

- **Quem decide:** Founder
- **Critério de aprovação:** estrutura criada, README mínimo, vínculos do workspace registrados.
- **Critério de retorno:** estrutura ambígua ou conflitante com convenção `teczilabs-` vs `teczi-`.

## 7. Skill associada

[`../skills/teczi-project-creation.md`](../skills/teczi-project-creation.md)

## 8. Operação manual (Stage 0)

1. Founder declara intenção e codinome.
2. Leo decide se é projeto novo ou se cabe em projeto existente.
3. Se novo: Denis sugere estrutura de pastas (`teczilabs-*` ou `teczi-*` conforme convenção).
4. Founder confirma codinome e estrutura.
5. Denis cria README inicial + vínculos no workspace.
6. Founder valida → PDOC concluído.

## 9. Anti-padrões

- Criar projeto sem codinome definido pelo Founder.
- Misturar convenção `teczilabs-*` (canônico cross-sistemas) com `teczi-*` (aplicações/ecossistemas).
- Pular PDOC e tentar iniciar DISC sem estrutura.
- Inferir documentação completa antes da DISC — PDOC é apenas terreno.

## 10. Referências

- SCOPE-FINAL §6.1
- Skill: [`../skills/teczi-project-creation.md`](../skills/teczi-project-creation.md)
- Memória workspace: `naming-teczilabs-vs-teczi.md`
- Próxima fase: [`02-DISC.md`](02-DISC.md)
