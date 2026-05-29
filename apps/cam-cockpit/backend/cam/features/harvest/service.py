"""
Service da feature harvest — lógica de aplicação.

REGRA FUNDAMENTAL: Harvest não é automático.
POST /api/v1/harvest/execute exige founder_approved=True (R4.07).

O sistema calcula e propõe — o Founder decide.
"""

from cam._shared.domain.primitives import Money
from cam.features.harvest.domain import (
    BUFFER_BASELINE,
    HarvestCalculator,
    HarvestProposal,
    SangriaCalculator,
    SangriaResult,
)


class HarvestService:
    def __init__(self, repo: object) -> None:
        self.repo = repo

    async def calculate_proposal(self, month: str) -> HarvestProposal:
        """
        Calcula proposta de harvest mensal.

        Não executa — apenas calcula. Gate Founder para execução (R4.07).
        """
        net_profit = await self.repo.get_net_monthly_profit(month=month)
        buffer_current = await self.repo.get_buffer_current()

        calc = HarvestCalculator(
            net_monthly_profit=net_profit,
            buffer_current=buffer_current,
            buffer_baseline=Money(BUFFER_BASELINE),
        )
        proposal = calc.calculate()
        await self.repo.save_proposal(month=month, proposal=proposal)
        return proposal

    async def execute_harvest(
        self, proposal_id: str, founder_approved: bool
    ) -> None:
        """
        Executa harvest após aprovação do Founder.

        Requer founder_approved=True — sem isso, levanta ValueError.
        Proteção constitucional: harvest não é automático (R4.07).
        """
        if not founder_approved:
            raise ValueError(
                "Harvest requer founder_approved=True explícito. "
                "O sistema apenas propõe a distribuição — a execução "
                "requer confirmação do Founder (SPEC R4.07)."
            )

        proposal = await self.repo.get_proposal(proposal_id)
        if proposal is None:
            raise ValueError(f"Proposta de harvest {proposal_id} não encontrada.")

        # Registra as transações nos buckets
        await self.repo.save_transactions(proposal=proposal, proposal_id=proposal_id)

    async def check_sangria(self) -> SangriaResult | None:
        """Verifica se o Bucket Derivativo precisa de sangria (≥ R$ 4.500)."""
        bucket_current = await self.repo.get_bucket_derivativo_current()
        bucket_baseline = await self.repo.get_bucket_derivativo_baseline()

        calc = SangriaCalculator(
            bucket_derivativo_current=bucket_current,
            bucket_derivativo_baseline=bucket_baseline,
        )
        return calc.calculate()

    async def get_buckets(self) -> dict:
        """Retorna saldos atuais dos 3 buckets."""
        return await self.repo.get_bucket_balances()

    async def get_history(self) -> list[dict]:
        """Retorna histórico de harvests executados."""
        return await self.repo.get_harvest_history()

    async def handle_darf_paid(self, event: object) -> None:
        """
        T-TD-005 — Handler de DarfPaid (SPEC v0.3).

        Quando DARF e marcada como paga, recalcula snapshot de buckets:
        - Apuracao do mes esta fechada → lucro liquido disponivel
        - Proposta de harvest fica visivel no painel /harvest
        - Execucao real ainda exige gate Founder (SPEC R4.07)
        """
        month = getattr(event, "month", None)
        if month:
            # v0.3 — chamada de recalculo lazy; persistencia real em SPEC v0.4
            try:
                await self.calculate_proposal(month)
            except Exception:
                # nao deve derrubar o subscriber (Art. 19 — fail-safe)
                pass
