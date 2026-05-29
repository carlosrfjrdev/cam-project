"""
AnalystDataCollector — Coleta de dados read-only para a IA Auditora.

ZERO ESCRITA. Este módulo contém exclusivamente operações de leitura.
Acesso somente às tabelas autorizadas: journal, decisões do Risk Engine
e violações.

Arts. 34-36: A IA opera em modo read-only. Qualquer tentativa de escrita
deve ser bloqueada pelo design (sem métodos de escrita nesta classe).

TASK-018 (BL-C SPEC v0.4): conecta a `cam_journal_entries`,
`cam_risk_decisions`, `cam_violations` via SQL bruto.
Compatível com modo offline: se session_factory for None, retorna [] (legacy).
"""


class AnalystDataCollector:
    """
    Coleta dados read-only para análise da IA Auditora.

    Métodos disponíveis: apenas leitura (get_*).
    Métodos proibidos: save, create, update, delete, insert — nenhum presente.
    """

    def __init__(self, session_factory=None) -> None:
        self.session_factory = session_factory

    async def get_journal_entries_today(self, date: str) -> list[dict]:
        if self.session_factory is None:
            return []
        from sqlalchemy import text as _text
        async with self.session_factory() as session:
            result = await session.execute(
                _text(
                    "SELECT asset, direction, result_net "
                    "FROM cam_journal_entries WHERE DATE(created_at) = :d"
                ),
                {"d": date},
            )
            return [dict(r._mapping) for r in result.fetchall()]

    async def get_risk_decisions_today(self, date: str) -> list[dict]:
        if self.session_factory is None:
            return []
        from sqlalchemy import text as _text
        async with self.session_factory() as session:
            # cam_risk_decisions tem coluna `decision` (APPROVED|REJECTED)
            # em vez de `approved` bool — normaliza para dict consumível.
            result = await session.execute(
                _text(
                    "SELECT validator, reason, "
                    "       (decision = 'APPROVED') AS approved "
                    "FROM cam_risk_decisions WHERE DATE(created_at) = :d"
                ),
                {"d": date},
            )
            return [dict(r._mapping) for r in result.fetchall()]

    async def get_violations_today(self, date: str) -> list[dict]:
        if self.session_factory is None:
            return []
        from sqlalchemy import text as _text
        async with self.session_factory() as session:
            # cam_violations tem `rule` + `context` JSONB, não `type`/`description`.
            result = await session.execute(
                _text(
                    "SELECT rule AS type, context::text AS description, "
                    "       created_at AS timestamp "
                    "FROM cam_violations WHERE DATE(created_at) = :d"
                ),
                {"d": date},
            )
            return [dict(r._mapping) for r in result.fetchall()]

    async def aggregate_metrics_today(self, date: str) -> dict:
        """TASK-018 — agregadores de aderência média + total trades."""
        entries = await self.get_journal_entries_today(date)
        decisions = await self.get_risk_decisions_today(date)
        approved = [d for d in decisions if d.get("approved")]
        return {
            "total_trades": len(entries),
            "decisions_approved": len(approved),
            "decisions_rejected": len(decisions) - len(approved),
        }
