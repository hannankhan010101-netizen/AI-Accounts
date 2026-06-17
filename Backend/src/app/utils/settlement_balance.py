"""Unallocated settlement balance after allocations and advance returns."""

from __future__ import annotations

from decimal import Decimal


def settlement_unallocated(
    *,
    total: Decimal,
    allocated: Decimal,
    returned: Decimal = Decimal(0),
) -> Decimal:
    """Remaining advance on a receipt or payment voucher."""

    return total - allocated - returned
