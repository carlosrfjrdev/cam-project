"""
Testes TDD do Bloco D — T-D03.
Cobre: Reconciler — match exato, sem match, múltiplos matches.
"""
from decimal import Decimal


class TestReconciliation:
    def test_exact_match_found(self):
        from cam.features.profit_integration.reconciliation import Reconciler

        manual = [{"id": "m1", "asset": "WIN", "result_gross": Decimal("400")}]
        csv_entries = [{"hash": "h1", "asset": "WIN", "result_gross": Decimal("400")}]
        r = Reconciler()
        report = r.reconcile(
            date="2026-05-24", manual_entries=manual, csv_entries=csv_entries
        )
        assert len(report.matched) == 1
        assert report.matched[0].confidence >= 0.9

    def test_no_match_returns_unmatched(self):
        from cam.features.profit_integration.reconciliation import Reconciler

        r = Reconciler()
        report = r.reconcile(
            date="2026-05-24",
            manual_entries=[],
            csv_entries=[{"hash": "h1", "asset": "WIN"}],
        )
        assert len(report.unmatched_csv) == 1

    def test_empty_both_returns_clean_report(self):
        from cam.features.profit_integration.reconciliation import Reconciler

        r = Reconciler()
        report = r.reconcile(date="2026-05-24", manual_entries=[], csv_entries=[])
        assert len(report.matched) == 0
        assert len(report.unmatched_manual) == 0
        assert len(report.unmatched_csv) == 0
        assert report.date == "2026-05-24"

    def test_unmatched_manual_when_no_csv(self):
        from cam.features.profit_integration.reconciliation import Reconciler

        manual = [{"id": "m1", "asset": "WIN", "result_gross": Decimal("400")}]
        r = Reconciler()
        report = r.reconcile(date="2026-05-24", manual_entries=manual, csv_entries=[])
        assert "m1" in report.unmatched_manual

    def test_match_confidence_is_exact_when_same_asset_and_result(self):
        from cam.features.profit_integration.reconciliation import Reconciler

        manual = [{"id": "m1", "asset": "WDO", "result_gross": Decimal("50")}]
        csv_entries = [{"hash": "h2", "asset": "WDO", "result_gross": Decimal("50")}]
        r = Reconciler()
        report = r.reconcile(
            date="2026-05-24", manual_entries=manual, csv_entries=csv_entries
        )
        assert report.matched[0].matched_by == "exact"
        assert report.matched[0].confidence == 1.0

    def test_multiple_manual_multiple_csv_match_pairs(self):
        from cam.features.profit_integration.reconciliation import Reconciler

        manual = [
            {"id": "m1", "asset": "WIN", "result_gross": Decimal("400")},
            {"id": "m2", "asset": "WDO", "result_gross": Decimal("50")},
        ]
        csv_entries = [
            {"hash": "h1", "asset": "WIN", "result_gross": Decimal("400")},
            {"hash": "h2", "asset": "WDO", "result_gross": Decimal("50")},
        ]
        r = Reconciler()
        report = r.reconcile(
            date="2026-05-24", manual_entries=manual, csv_entries=csv_entries
        )
        assert len(report.matched) == 2
        assert len(report.unmatched_manual) == 0
        assert len(report.unmatched_csv) == 0
