# Feature: journal

## Propósito

Registro imutável de todas as operações realizadas pelo CaM. Falha de registro é falha operacional (Art. 31º). Implementa journal duplo: banco PostgreSQL + arquivo JSONL append-only.

## Artigos Constitucionais

- **Art. 31º** — Operação sem registro no journal é falha operacional
- **Art. 25º** — Resultado exibido LÍQUIDO de imposto provisionado (nunca apenas bruto)
- **Art. 19º** — Journal duplo: banco + JSONL em `~/.cam/journal/` (fallback com posição aberta)

## I/O

**Inputs:**
- `POST /api/v1/journal/entries` — criação manual
- `POST /api/v1/journal/import-csv` — importação CSV do Profit (F2)
- `GET /api/v1/journal/entries` — listagem com filtros
- `GET /api/v1/journal/reports/{tipo}` — relatórios diário/semanal/mensal/estratégia/ativo
- `GET /api/v1/journal/export` — exportação CSV/JSON

**Imutabilidade:** sem UPDATE nem DELETE em `cam_journal_entries`. Correções via entrada de correção referenciando a entrada original.

## Eventos Publicados

- `JournalEntryCreated` — consumido por `fiscal` (atualiza provisão) e `notifications`

## Anti-padrões

- UPDATE ou DELETE em `cam_journal_entries` — proibição absoluta no repository
- Exibir resultado bruto sem mostrar o líquido (Art. 25º)
- Criar entry sem todos os campos obrigatórios da SPEC §6.2
- IA escrever entries no journal (Art. 35º)

## Cálculo de Resultado

```
resultado_liquido = resultado_bruto - custos - imposto_provisionado
imposto_provisionado = resultado_bruto * 0.20 se resultado_bruto > 0, else 0
```
