"""
Reconciliação entre entradas manuais do Journal e CSV do Profit (F2).

Compara JournalEntries criados manualmente pelo operador com as linhas
importadas do CSV do Profit para identificar:
    - Matches exatos (mesmo ativo + resultado)
    - Entradas manuais sem correspondência no CSV
    - Linhas do CSV sem correspondência manual

Algoritmo:
    1. Para cada manual_entry, busca csv_entry com mesmo asset + result_gross
    2. Match encontrado → ReconciliationMatch(confidence=1.0, matched_by="exact")
    3. Sem match → entrada vai para unmatched_manual ou unmatched_csv

Extensão futura: match aproximado por resultado próximo (fuzzy), data/hora.
"""
from dataclasses import dataclass


@dataclass
class ReconciliationMatch:
    """Par manual↔CSV identificado na reconciliação."""

    manual_entry_id: str
    csv_entry_hash: str
    confidence: float  # 0.0–1.0
    matched_by: str    # "exact" | "approximate"


@dataclass
class ReconciliationReport:
    """Relatório completo de reconciliação para uma data."""

    date: str
    matched: list[ReconciliationMatch]
    unmatched_manual: list[str]        # IDs de entradas manuais sem par CSV
    unmatched_csv: list[dict]          # Entradas CSV sem par manual


class Reconciler:
    """
    Reconcilia JournalEntries manuais com linhas do CSV do Profit.

    Critério de match exato:
        - Mesmo asset (ex.: "WIN")
        - Mesmo result_gross (Decimal)
    """

    def reconcile(
        self,
        date: str,
        manual_entries: list[dict],
        csv_entries: list[dict],
    ) -> ReconciliationReport:
        """
        Executa reconciliação para uma data.

        Parâmetros:
            date: string YYYY-MM-DD identificando o pregão
            manual_entries: lista de dicts com "id", "asset", "result_gross"
            csv_entries: lista de dicts com "hash", "asset", "result_gross"

        Retorna ReconciliationReport com matched, unmatched_manual e unmatched_csv.
        """
        matched: list[ReconciliationMatch] = []
        unmatched_manual: list[str] = []
        unmatched_csv: list[dict] = list(csv_entries)  # cópia mutável

        for manual in manual_entries:
            found = self._find_match(manual, unmatched_csv)
            if found is not None:
                match_obj, csv_entry = found
                matched.append(match_obj)
                unmatched_csv.remove(csv_entry)
            else:
                unmatched_manual.append(manual["id"])

        return ReconciliationReport(
            date=date,
            matched=matched,
            unmatched_manual=unmatched_manual,
            unmatched_csv=unmatched_csv,
        )

    def _find_match(
        self,
        manual: dict,
        csv_pool: list[dict],
    ) -> tuple[ReconciliationMatch, dict] | None:
        """
        Tenta encontrar match exato para uma entrada manual na pool de CSV.

        Critério: mesmo asset E mesmo result_gross.
        Retorna (ReconciliationMatch, csv_entry) ou None.
        """
        manual_asset = manual.get("asset", "")
        manual_result = manual.get("result_gross")

        for csv_entry in csv_pool:
            csv_asset = csv_entry.get("asset", "")
            csv_result = csv_entry.get("result_gross")

            if manual_asset == csv_asset and manual_result == csv_result:
                return (
                    ReconciliationMatch(
                        manual_entry_id=manual["id"],
                        csv_entry_hash=csv_entry.get("hash", ""),
                        confidence=1.0,
                        matched_by="exact",
                    ),
                    csv_entry,
                )

        return None
