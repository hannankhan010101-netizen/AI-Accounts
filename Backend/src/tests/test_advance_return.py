"""Settlement unallocated balance helper."""

from decimal import Decimal

from app.utils.settlement_balance import settlement_unallocated


def test_unallocated_after_return() -> None:
    balance = settlement_unallocated(
        total=Decimal("1000"),
        allocated=Decimal("400"),
        returned=Decimal("200"),
    )
    assert balance == Decimal("400")


def test_unallocated_cannot_exceed_total() -> None:
    balance = settlement_unallocated(
        total=Decimal("500"),
        allocated=Decimal("500"),
        returned=Decimal("0"),
    )
    assert balance == Decimal("0")
