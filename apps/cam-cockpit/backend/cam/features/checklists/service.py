"""
Service da feature checklists — lógica de aplicação.

Valida que o checklist está completo antes de salvar.
Um checklist incompleto não pode ser persistido — o Risk Engine depende disso.
"""
from cam.features.checklists.domain import PostMarketChecklist, PreMarketChecklist


class ChecklistService:
    def __init__(self, repo: object) -> None:
        self.repo = repo

    async def save_pre_market(self, date: str, items: dict[str, bool]) -> None:
        """
        Salva checklist pré-mercado.

        Rejeita com ValueError se o checklist não estiver completo.
        Todos os itens obrigatórios devem estar marcados como True.
        """
        checklist = PreMarketChecklist(date=date, items=items)
        if not checklist.is_complete():
            raise ValueError(
                "Checklist pré-mercado incompleto — todos os itens obrigatórios "
                "devem ser preenchidos antes de operar (SPEC R10.05)."
            )
        await self.repo.save_pre_market(checklist)

    async def save_post_market(
        self,
        date: str,
        items: dict[str, bool],
        result_summary: dict | None = None,
    ) -> None:
        """
        Salva checklist pós-mercado.

        Rejeita com ValueError se o checklist não estiver completo.
        """
        checklist = PostMarketChecklist(
            date=date, items=items, result_summary=result_summary
        )
        if not checklist.is_complete():
            raise ValueError(
                "Checklist pós-mercado incompleto — todos os itens obrigatórios "
                "devem ser preenchidos ao encerrar o pregão (SPEC R10.05)."
            )
        await self.repo.save_post_market(checklist)

    async def get_pre_market(self, date: str) -> PreMarketChecklist | None:
        """Retorna checklist pré-mercado de uma data."""
        return await self.repo.get_pre_market(date=date)

    async def get_post_market(self, date: str) -> PostMarketChecklist | None:
        """Retorna checklist pós-mercado de uma data."""
        return await self.repo.get_post_market(date=date)
