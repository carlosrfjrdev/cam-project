---
skill: teczi-project-creation
phase: PDOC
status: draft
lead_persona: Leo + Denis
canonical_source: projects/devflow/SCOPE-FINAL-V6.0-NCC-1701.md
---

# Skill — teczi-project-creation

## 1. Propósito

Criar e registrar um novo projeto no ecossistema Teczilabs: codinome, estrutura física, README mínimo, vínculos com `teczilabs/produtos/`.

## 2. Quando acionar

- Founder declara intenção de novo projeto/produto/frente cross-produto.
- **Não acionar** quando o projeto já existe.

## 3. Entradas esperadas

- Intenção do Founder (texto livre).
- Codinome proposto.
- Domínio inicial (produto/cliente/contexto).
- Convenção de nomenclatura aplicável (`teczilabs-*` canônico cross-sistemas vs `teczi-*` aplicação/ecossistema).

## 4. Saídas esperadas

- Estrutura de pastas criada.
- README inicial.
- Vínculo com `teczilabs/produtos/{produto}/` se aplicável.
- Notas iniciais de contexto em `/projects/{produto}/notes/`.

## 5. Operação manual hoje (Stage 0)

1. Founder fala: "Vamos criar projeto X com codinome Y".
2. Leo decide se cabe em projeto existente ou se é novo.
3. Denis sugere estrutura conforme convenção.
4. Founder confirma.
5. Denis cria README + vínculos.
6. Founder valida → PDOC concluído.

## 6. Contrato esperado quando implementada

```yaml
inputs:
  required:
    - intent: string
    - codename: string
    - domain: string
  optional:
    - parent_project_id: string
outputs:
  - project_id: string
  - root_path: string
  - readme_path: string
  - workspace_links: array
tools_allowed:
  - fs.write (scoped to /projects, /teczi-*, /teczilabs-*)
  - codex.project.create (futuro)
tools_forbidden:
  - git.push
  - repo.write_source_code
gate:
  required_approval: Founder
abstention_rules:
  - missing_codename
  - convention_conflict (teczilabs- vs teczi-)
  - existing_project_with_same_codename
token_budget_heuristic: low
```

## 7. Anti-padrões

- Criar projeto sem codinome explícito do Founder.
- Inferir convenção quando há ambiguidade — sempre confirmar.
- Gerar documentação extensa em PDOC — é apenas terreno.

## 8. Referências

- Fase: [`../phases/01-PDOC.md`](../phases/01-PDOC.md)
- Memória: `naming-teczilabs-vs-teczi.md`
- SCOPE-FINAL §6.1
