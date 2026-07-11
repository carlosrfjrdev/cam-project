---
template: SCOPE (frontend · complementar)
phase: P&D / Research Lane
status: Draft 1.0
produto: CaM
codinome: research-cubo-leadlag · frontend ("Quant Lab")
complementa: CaM-RESEARCH-CUBO-LEADLAG.md (teses + scope backend)
vive_em: project/cam-cockpit/research/CaM-SCOPE-FRONTEND-CUBO.md
data: 2026-06-01
lead: Mentor de Estratégia / Product (criação) · Founder (aprovação)
---

# SCOPE Frontend — Quant Lab do Cubo de Lead-Lag

> Complementa o documento de teses + scope backend. Define **como** a descoberta vira
> interface operável no cockpit do CaM. É scope de **research**: read-only, isolado do
> live, sem nenhum caminho para envio de ordem ou parametrização do Risk Engine.

---

## 1. Princípios de produto

1. **Quant Lab ≠ Cockpit Live.** Área distinta, modo mental distinto (explorar vs operar). Navegação e visual separados, com **badge "RESEARCH"** sempre visível (análogo ao badge PAPER vermelho do live), para nunca confundir.
2. **Read-only sobre dado de research.** Nenhuma tela aqui dispara ordem, toca `cam_orders/positions`, ou ajusta o Risk Engine. Consome **artefatos computados** da research lane.
3. **A UI força a honestidade.** Métrica de manchete é **expectância líquida** (após custos+IR), nunca taxa de acerto. **DSR** e **contador de tentativas** são cidadãos de primeira classe. O **checklist Go/No-Go** aparece literalmente como checklist com pass/fail. A interface é desenhada para dificultar o autoengano.
4. **Consome resumo, não tick cru.** Heatmaps, curvas e janelas de evento são agregados leves vindos do backend. O streaming de tick/book cru continua no **inspector** já existente — o Quant Lab não re-renderiza milhões de ticks.
5. **Async por natureza.** Rodadas de cubo são jobs pesados: progresso via WebSocket, cancelável, resultados persistidos e reprodutíveis.

---

## 2. Arquitetura de navegação

Novo top-level **Quant Lab**, irmão do Cockpit. Sub-rotas:

```
/lab
  /lab/explorer            → Cube Explorer (peça central)
  /lab/cell/:runId/:F/:D/:tau  → Cell Detail (dossiê de evidência)
  /lab/runs                → Run Registry (experimentos)
  /lab/runs/new            → Run Launcher (config + pré-registro)
  /lab/fib/:runId/:cell    → Fib A/B (Tese 2)
  /lab/data-health         → Cobertura e clock-sync (cresce no R0)
  /lab/synthesis           → Regime × Trigger (R4)
```

Badge RESEARCH no header da área inteira. Cor/tema próprios para reforçar o modo.

---

## 3. As telas

### 3.1 Cube Explorer — peça central
Renderiza o tensor 3D como **fatia 2D + scrubber**:

- **Controles de topo:** lente (rápida/lenta), timeframe (lenta), **métrica** exibida (ρ defasado, $\hat\mu_h$ no horizonte escolhido, DSR, p-valor ajustado), e qual **eixo é o slider** (default: lag τ).
- **Heatmap:** linhas = fontes, colunas = alvos; cor = métrica na fatia de lag atual. **Colormap divergente** (sinal importa: negativo↔positivo). Hover → valor + n amostras.
- **Slider de lag:** ao arrastar τ, o heatmap atualiza — você **vê a propagação emergir** com a defasagem. (esse é o pulo do gato para enxergar o 3º eixo.)
- **Toggle "só sobreviventes":** mostra apenas células que passam FDR/DSR + n mínimo. Filtro de significância e de capacidade.
- **Lista ranqueada lateral:** top células por expectância líquida, clicáveis.
- **Click numa célula → Cell Detail.**

### 3.2 Cell Detail — dossiê de evidência
Tudo que decide se a célula vive, num lugar só:

- **Header:** F→D, τ, valores correntes da métrica.
- **Curva de decaimento** ($\hat\mu_h$ vs $h$) com a **linha de latência $\lambda$ marcada** — visual direto do H4 (edge sobrevive à execução?).
- **Painel de event study:** trajetórias de retorno assinado alinhadas à janela do evento (média + banda de confiança); contagem de eventos.
- **Contraste lead-lag** $U(\theta)$ (lente rápida) mostrando o argmax → confirma a direção.
- **HY vs correlação ingênua:** overlay que demonstra visualmente o Epps morto (H5).
- **Card de veredito estatístico:** DSR, p ajustado (FDR), n amostras, quebra por regime.
- **Checklist Go/No-Go:** os 6 critérios (§6 do backend) como linhas com ✅/❌/⏳ + o valor de cada. **Centro de honestidade da tela.**
- (Lente lenta) bloco de **Fib A/B** embutido quando aplicável.

### 3.3 Run Launcher — config + pré-registro
Formulário que **é** o pré-registro da hipótese (anti data-snooping):

- Lente, universo (multi-select de ativos), alvo(s), conjunto-fonte(s), timeframe(s), grade de τ/δ, intervalo de datas.
- Limiares: κ (evento), η (toque fib), θz/n (swing), φ (Kelly).
- Toggles: condicionamento por regime, controles de causa comum (WDO/ES).
- Esquema de validação: walk-forward (janelas/step) e purged CV/embargo.
- **Modelo de custo:** corretagem, emolumentos, slippage assumido (expectância é líquida).
- Ao submeter: registra hipótese + params de forma **imutável** e enfileira o job.

### 3.4 Run Registry — rastreamento de experimentos
- Tabela de rodadas: id, data, resumo de params, status (queued/running/done/failed/killed), resultado de manchete, DSR, **nº de células testadas**.
- **Contador global de tentativas** em destaque — total de hipóteses testadas em todas as rodadas, alimentando a deflação do DSR. A UI lembra: "você testou X hipóteses; o DSR já está ajustado". Faz a estatística honesta ser inevitável.
- **Reprodutibilidade:** cada rodada fixada a snapshot de dado + hash de params + versão de código.
- Ações: ver, re-rodar, cancelar (running), arquivar.

### 3.5 Fib A/B (Tese 2)
Comparação lado a lado **baseline (sem fib)** × **augmentado (com fib)**:
- $\hat\mu_A$ vs $\hat\mu_B$, com $\Delta=\hat\mu_B-\hat\mu_A$ destacado e sua significância OOS.
- Resultado do **controle de redundância** (o coeficiente do fib sobrevive a "também é máx/mín / número redondo / nó de volume"?).
- Veredito explícito: **FIB FICA** ou **FIB CAI → usar baseline**.

### 3.6 Regime × Trigger — síntese (R4)
Visualização do sistema de duas camadas: estado de regime da lente lenta (porteiro) sobreposto aos gatilhos de fluxo da lente rápida sobre um ativo. Reusa o componente de chart do inspector com marcadores de evento. Mostra o edge da composição vs o das partes.

### 3.7 (Later) Live signal overlay — ponte para paper
Quando uma célula é promovida, sobrepor o sinal disparando no chart do inspector (read-only). Marcado como **Later** — pertence à fase paper/live, governada pelo pipeline padrão e pelo Risk Engine, não pela research.

---

## 4. Contratos Frontend ↔ Backend

Tudo namespaced sob `/research` — read-only em relação ao live.

| Método | Endpoint | Uso |
|---|---|---|
| POST | `/research/runs` | lança rodada (retorna `run_id`) |
| GET | `/research/runs` | lista de rodadas + status |
| GET | `/research/runs/{id}` | status + sumário de resultado |
| DELETE | `/research/runs/{id}` | cancela/arquiva |
| GET | `/research/runs/{id}/cube?metric=&lens=&lag=` | fatia do cubo para o heatmap |
| GET | `/research/cells/{id}/{F}/{D}/{tau}` | dossiê completo da célula |
| GET | `/research/runs/{id}/fib-ab/{cell}` | comparação baseline vs fib |
| GET | `/research/stats/trials` | contador global de tentativas (DSR) |
| GET | `/research/data-health` | cobertura + status de clock-sync |
| WS | `/research/runs/{id}/progress` | eventos de progresso/conclusão |

Payloads do heatmap = matriz de escalares (leve). Decay = ~dezenas de pontos. Event study = média + banda. **Nunca** tick cru.

---

## 5. Componentes e libs (alinhado à stack atual)

- **React SPA + Vite** (existente). Sem SSR.
- **Heatmap do cubo:** `visx` (D3 composável) ou `plotly` (heatmap interativo com hover/zoom nativos — bom encaixe para ferramenta de research). Decisão em ADR leve.
- **Curvas (decaimento, distribuição, expectância):** **Recharts** (já em uso).
- **Chart de preço + overlay de evento (synthesis/live):** **TradingView Lightweight Charts** (já em uso) — **reusa o componente do inspector**.
- **WebSocket:** cliente nativo sobre o WS do FastAPI (já em uso para P&L live).
- **Estado:** seguir o padrão atual do frontend; o Explorer precisa de estado de slicing/filtro coeso.

---

## 6. Estados, performance e dados

- **Async/jobs:** Launcher enfileira; Registry e Explorer mostram progresso via WS; cancelamento suportado.
- **Estados de tela:** loading (rodada longa com progresso), empty (nenhuma rodada/célula), error (job falhou), **killed** (célula reprovada — exibir o porquê do Go/No-Go).
- **Performance:** o frontend só consome agregados computados; raw tick fica no inspector. Heatmaps e curvas são leves por design.
- **Reprodutibilidade:** resultado sempre amarrado a snapshot + params hash + versão.

---

## 7. Dentro / Fora / Depois

**Dentro (In)**
- Área Quant Lab com badge RESEARCH e isolamento de navegação.
- Cube Explorer (heatmap + slider de lag + filtro de sobreviventes + ranking).
- Cell Detail com decaimento, event study, contraste lead-lag, HY vs ingênua, veredito e **checklist Go/No-Go**.
- Run Launcher (pré-registro) + Run Registry (com contador global de tentativas).
- Fib A/B.
- Data Health (cobertura + clock-sync).

**Fora (Out)**
- Qualquer disparo de ordem ou ajuste de Risk Engine pela UI.
- Re-render de tick cru no Quant Lab (responsabilidade do inspector).
- Edição manual de resultado/estatística (resultado é imutável por rodada).
- Multi-usuário / colaboração.

**Depois (Later)**
- Live signal overlay no chart do inspector (ponte para paper).
- Synthesis Regime × Trigger em produção (R4).
- Exportação de relatório (PDF) de uma rodada.
- Comparador multi-rodada (diff de params e resultados).

---

## 8. Fases (a UI cresce com o backend)

| Fase UI | Acompanha backend | Entrega |
|---|---|---|
| **UI-R0** | R0 (dados) | Data Health: cobertura + status de clock-sync |
| **UI-R2** | R2 (cubo rápido) | Cube Explorer + Cell Detail + Launcher + Registry |
| **UI-R3** | R3 (cubo lento) | Toggle de lente lenta/timeframe + Fib A/B |
| **UI-R4** | R4 (síntese) | Synthesis Regime × Trigger |
| **UI-Later** | paper/live | Live signal overlay (governado pelo pipeline padrão) |

---

## 9. Decisões abertas do Founder

- **Lib de heatmap:** `plotly` (interatividade pronta) vs `visx` (controle fino, leve). → ADR.
- **Tema/identidade do modo RESEARCH:** seguir design system do cockpit com variação, ou visual próprio?
- **Granularidade do contador de tentativas:** por célula, por rodada, ou ambos, para alimentar o DSR?
- **Persistência de runs:** mesmo Postgres do CaM (tabelas `research_*` namespaced) ou store separado? (mantendo isolamento do live).
- **Janela default do event study** exibida na Cell Detail (alinhar com a grade de τ/δ definida no backend).

---

## 10. Histórico de versões

| Versão | Data | Mudança | Aprovado por |
|---|---|---|---|
| 1.0 | 2026-06-01 | Draft inicial do scope de frontend (Quant Lab) | (pendente Founder) |
