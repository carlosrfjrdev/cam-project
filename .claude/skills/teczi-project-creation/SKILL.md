---
name: teczi-project-creation
description: "PDOC do Teczi DevFlow NCC-1701 (Leo + Denis). Acionar quando o Founder declarar intenção de criar novo projeto/aplicativo/frente cross-produto no CaM — registra projeto, cria estrutura de pastas em /project/{codinome}/ e /apps/{codinome}/, produz README mínimo. Não acionar quando o projeto já existe."
phase: PDOC
lead_persona: Leo + Denis
status: draft (Stage 0 — execução manual via Founder)
---

# Skill — teczi-project-creation (Fase 1: PDOC)

> Skill da Fase 1 (PDOC) do Teczi DevFlow NCC-1701, portada para o contexto **CaM**. Lead: **Leo + Denis**. Stage 0 — execução documental disciplinada com Founder-only no gate.

## 1. Propósito

Criar e registrar um novo projeto/aplicativo no CaM: codinome, estrutura física (`/project/{codinome}/` + `/apps/{codinome}/`), README mínimo, vínculo com a Constituição.

## 2. Quando acionar

- Founder declara intenção de novo aplicativo do cockpit (Risk Engine, Journal, Backtest, UI, etc.) ou frente cross-produto.
- **Não acionar** quando o projeto já existe.

## 3. Entradas esperadas

- Intenção do Founder (texto livre).
- Codinome proposto (kebab-case, prefixo `cam-` recomendado).
- Camada/domínio inicial (frontend / backend / engine / integração).

## 4. Saídas esperadas

- Pasta `/project/{codinome}/` criada (artefatos DevFlow).
- Pasta `/apps/{codinome}/` criada (código futuro).
- `README.md` inicial em cada pasta.
- Notas iniciais de contexto em `/project/{codinome}/notes/` (se houver).

## 5. Operação manual hoje (Stage 0)

1. Founder fala: "Vamos criar app X com codinome `cam-Y`".
2. Leo decide se cabe em projeto existente ou se é novo.
3. Denis sugere estrutura conforme convenção CaM (`cam-*` para aplicativos do cockpit).
4. Founder confirma.
5. Denis cria pastas + READMEs + vínculos.
6. Founder valida → PDOC concluído → segue para DISC (se ambíguo) ou SPEC (se claro).

## 6. Contrato esperado quando implementada (futuro)

```yaml
inputs:
  required: [intent, codename, layer]
  optional: [parent_project_id]
outputs: [project_id, project_path, app_path, readme_paths]
tools_allowed:
  - fs.write (scoped to /project, /apps)
tools_forbidden:
  - repo.write_source_code
  - git.push.main
gate:
  required_approval: Founder
abstention_rules:
  - missing_codename
  - existing_project_with_same_codename
  - conflict_with_constituicao (ex.: app que viola Arts. 11/15/18/25/35)
token_budget_heuristic: low
```

## 7. Anti-padrões

- Criar projeto sem codinome explícito do Founder.
- Inferir convenção quando há ambiguidade — sempre confirmar.
- Gerar documentação extensa em PDOC — é apenas terreno.
- Criar app que viola a Constituição (Risk Engine bypass, IA executando ordem, etc.).

## 8. Referências

- Fase: [`../../../teczi-devflow/NCC-1701/phases/01-PDOC.md`](../../../teczi-devflow/NCC-1701/phases/01-PDOC.md)
- Constituição: [`../../../CONSTITUICAO.md`](../../../CONSTITUICAO.md) — Art. 1º (natureza), Anexo II (Fase 0)
- Convenção: prefixo `cam-` para aplicativos do cockpit
