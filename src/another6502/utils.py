"""Utilities to unspecific for other modules."""

from typing import Never


def assert_never(arg: Never) -> Never:  # noqa: ARG001
    """Help the type checker perform exhaustiveness checks."""
    raise AssertionError


def dec_to_bcd(dec: int) -> int:
    """Convert a decimal number to binary-coded decimal (BCD)."""
    if dec < 0 or dec > 99:  # noqa: PLR2004
        msg = "Decimal number must be between 0 and 99 inclusive."
        raise ValueError(msg)

    tens = dec // 10
    ones = dec % 10
    return (tens << 4) | ones
