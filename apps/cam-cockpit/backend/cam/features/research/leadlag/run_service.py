"""
Serviço de RUN da análise lead-lag — SPEC v0.5.2 (R-20/R-22/R-25/R-30/R-31).

Orquestra: lê séries de research_*, computa correlação defasada bar-time
`C_{F→D}(δ)` (e event study quando o alvo tem retornos) sobre a grade de δ
parametrizável, persiste em research_runs/research_run_results com o contador de
tentativas honesto. Read-only sobre o live; escreve só em research_*.

Análise é DESCRITIVA (R-33): correlação, n, δ, expectância, veredito. Nunca
sinal/ordem/sizing.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker

from cam._shared.research_kernel import validation
from cam.features.research.leadlag import analysis
from cam.features.research.leadlag import repository as repo


class LeadLagRunService:
    def __init__(self, session_factory: async_sessionmaker[Any]) -> None:
        self._factory = session_factory

    async def run(
        self,
        sources: list[str],
        target: str,
        delta_grid: list[int],
        timeframe: str = "M1",
        min_samples: int = analysis.DEFAULT_MIN_SAMPLES,
        cost: float = 0.0,
        fdr_q: float = 0.05,
        snapshot_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Roda a análise bar-time para cada (fonte → alvo) na grade de δ.
        `delta_grid`: lookback em barras (ex.: até 50 — "últimos 50 timeframes").
        """
        srcs = [s.strip().upper() for s in sources if s.strip()]
        tgt = target.strip().upper()
        grid = sorted({d for d in delta_grid if d >= 1})
        n_trials = analysis.count_trials(len(srcs), 1, len(grid))

        async with self._factory() as session:
            run_id = await repo.create_run(
                session,
                snapshot_id=snapshot_id,
                lens="slow",
                mode="intraday",
                sources=srcs,
                target=tgt,
                delta_grid=grid,
                timeframes=[timeframe],
                n_trials=n_trials,
                status="running",
            )

            target_closes = await repo.bar_closes(session, tgt, timeframe)
            target_returns = analysis.log_returns(target_closes)

            # 1ª passada: mede correlação por célula (0.5.2).
            raw_cells: list[dict[str, Any]] = []
            for src in srcs:
                src_closes = await repo.bar_closes(session, src, timeframe)
                src_returns = analysis.log_returns(src_closes)
                n = min(len(src_returns), len(target_returns))
                cells = analysis.lag_profile(
                    src_returns[:n], target_returns[:n], grid, min_samples
                )
                for c in cells:
                    raw_cells.append({"src": src, "cell": c})

            # 2ª passada (0.5.3): validação estatística honesta.
            # - p-valor por célula OK; FDR (Benjamini-Hochberg) sobre TODAS as
            #   células OK (controla falsa descoberta no cubo varrido);
            # - DSR penalizando o nº REAL de tentativas (deflaciona snooping).
            ok_idx = [
                i for i, rc in enumerate(raw_cells) if rc["cell"].verdict == "OK"
            ]
            pvals = [
                validation.corr_pvalue(
                    raw_cells[i]["cell"].correlation, raw_cells[i]["cell"].n_samples
                )
                for i in ok_idx
            ]
            rejected = validation.benjamini_hochberg(pvals, q=fdr_q)
            survivors = {ok_idx[k] for k, r in enumerate(rejected) if r}
            fdr_by_idx = {ok_idx[k]: pvals[k] for k in range(len(ok_idx))}

            results: list[dict[str, Any]] = []
            n_survivors = 0
            for i, rc in enumerate(raw_cells):
                c = rc["cell"]
                dsr_val: float | None = None
                fdr_val: float | None = None
                verdict = c.verdict
                if c.verdict == "OK":
                    fdr_val = fdr_by_idx.get(i)
                    # DSR: trata a correlação como proxy de Sharpe da célula,
                    # deflacionada pelo nº de tentativas (descritivo — não autoriza).
                    dsr_val = validation.deflated_sharpe_ratio(
                        observed_sr=abs(c.correlation),
                        n_obs=c.n_samples,
                        skew=0.0,
                        kurtosis=3.0,
                        n_trials=n_trials,
                    )
                    if i in survivors:
                        verdict = "SURVIVOR"
                        n_survivors += 1
                    else:
                        verdict = "KILLED"  # não sobreviveu ao FDR
                results.append(
                    {
                        "run_id": run_id,
                        "source": rc["src"],
                        "target": tgt,
                        "timeframe": timeframe,
                        "delta": c.delta,
                        "correlation": (
                            None if c.verdict != "OK" else c.correlation
                        ),
                        "mu_net": None,
                        "n_samples": c.n_samples,
                        "dsr": dsr_val,
                        "fdr_q": fdr_val,
                        "verdict": verdict,
                    }
                )

            await repo.insert_results(session, results)
            if n_survivors > 0:
                status = "done"
            elif ok_idx:
                status = "killed"  # mediu, mas nada sobreviveu ao FDR (vitória honesta)
            else:
                status = "insufficient_data"
            await repo.set_run_status(session, run_id, status)
            await session.commit()

        return {
            "run_id": run_id,
            "n_trials": n_trials,
            "status": status,
            "sources": srcs,
            "target": tgt,
            "delta_grid": grid,
            "timeframe": timeframe,
            "cells": len(results),
            "survivors": n_survivors,
        }

    async def get_result(self, run_id: int) -> dict[str, Any] | None:
        async with self._factory() as session:
            run = await repo.get_run(session, run_id)
            if run is None:
                return None
            results = await repo.get_run_results(session, run_id)
            return {"run": run, "results": results}

    async def list_runs(self) -> list[dict[str, Any]]:
        async with self._factory() as session:
            return await repo.list_runs(session)

    async def total_trials(self) -> int:
        async with self._factory() as session:
            return await repo.total_trials(session)
