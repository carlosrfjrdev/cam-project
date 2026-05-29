"""
Testes TDD para o domínio da feature fiscal — T-C06.

Arts. 24º, 25º, 26º, 27º da Constituição.
"""
from decimal import Decimal


class TestFiscalApuration:
    def test_ir_calculated_on_positive_result(self):
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import FiscalApuration

        ap = FiscalApuration(
            month="2026-05",
            gross_result=Money(Decimal("1000.00")),
            costs=Money(Decimal("100.00")),
            irrf_retained=Money(Decimal("5.00")),
            loss_compensation=Money(Decimal("0.00")),
        )
        # net = 1000 - 100 = 900; IR = 900 * 20% = 180; DARF = 180 - 5 (irrf) = 175
        assert ap.net_result.amount == Decimal("900.00")
        assert ap.ir_due.amount == Decimal("180.00")
        assert ap.darf_value.amount == Decimal("175.00")

    def test_no_ir_on_loss(self):
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import FiscalApuration

        ap = FiscalApuration(
            month="2026-05",
            gross_result=Money(Decimal("-500.00")),
            costs=Money(Decimal("50.00")),
            irrf_retained=Money(Decimal("0.00")),
            loss_compensation=Money(Decimal("0.00")),
        )
        assert ap.ir_due.amount == Decimal("0.00")
        assert ap.darf_value.amount == Decimal("0.00")

    def test_loss_compensation_reduces_taxable_base(self):
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import FiscalApuration

        ap = FiscalApuration(
            month="2026-05",
            gross_result=Money(Decimal("1000.00")),
            costs=Money(Decimal("0.00")),
            irrf_retained=Money(Decimal("0.00")),
            loss_compensation=Money(Decimal("500.00")),  # prejuízo anterior
        )
        # taxable = 1000 - 500 = 500; IR = 500 * 20% = 100
        assert ap.ir_due.amount == Decimal("100.00")

    def test_net_result_excludes_costs(self):
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import FiscalApuration

        ap = FiscalApuration(
            month="2026-05",
            gross_result=Money(Decimal("600.00")),
            costs=Money(Decimal("60.00")),
            irrf_retained=Money(Decimal("0.00")),
            loss_compensation=Money(Decimal("0.00")),
        )
        assert ap.net_result.amount == Decimal("540.00")

    def test_irrf_reduces_darf_to_zero_minimum(self):
        """DARF não pode ser negativa — mínimo é zero."""
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import FiscalApuration

        ap = FiscalApuration(
            month="2026-05",
            gross_result=Money(Decimal("100.00")),
            costs=Money(Decimal("0.00")),
            irrf_retained=Money(Decimal("50.00")),  # IRRF maior que IR (hipotético)
            loss_compensation=Money(Decimal("0.00")),
        )
        # IR = 100 * 20% = 20; IRRF = 50; DARF = max(0, 20 - 50) = 0
        assert ap.darf_value.amount == Decimal("0.00")

    def test_taxable_base_never_negative(self):
        """Base tributável nunca negativa mesmo com compensação maior que resultado."""
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import FiscalApuration

        ap = FiscalApuration(
            month="2026-05",
            gross_result=Money(Decimal("200.00")),
            costs=Money(Decimal("0.00")),
            irrf_retained=Money(Decimal("0.00")),
            loss_compensation=Money(Decimal("500.00")),  # maior que resultado
        )
        # taxable = max(0, 200 - 500) = 0; IR = 0
        assert ap.taxable_base.amount == Decimal("0.00")
        assert ap.ir_due.amount == Decimal("0.00")


class TestDarfStatus:
    def test_darf_starts_as_pending(self):
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import Darf, DarfStatus

        darf = Darf(
            month="2026-05",
            value=Money(Decimal("100.00")),
            due_date="2026-07-31",
        )
        assert darf.status == DarfStatus.PENDING

    def test_overdue_darf_blocks_compliance(self):
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import Darf, DarfStatus

        darf = Darf(
            month="2026-05",
            value=Money(Decimal("100.00")),
            due_date="2026-07-31",
            status=DarfStatus.OVERDUE,
        )
        # Art. 26º: DARF OVERDUE bloqueia operações
        assert not darf.is_compliant()

    def test_paid_darf_is_compliant(self):
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import Darf, DarfStatus

        darf = Darf(
            month="2026-05",
            value=Money(Decimal("100.00")),
            due_date="2026-07-31",
            status=DarfStatus.PAID,
        )
        assert darf.is_compliant()

    def test_pending_darf_is_compliant(self):
        """DARF PENDING (ainda não vencida) não bloqueia operações."""
        from cam._shared.domain.primitives import Money
        from cam.features.fiscal.domain import Darf, DarfStatus

        darf = Darf(
            month="2026-05",
            value=Money(Decimal("100.00")),
            due_date="2026-07-31",
            status=DarfStatus.PENDING,
        )
        assert darf.is_compliant()
