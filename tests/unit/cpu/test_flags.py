"""Test instructions that set and store status register flags."""


import pytest

from emulator.cpu import CPU6502


@pytest.mark.parametrize(
    ("a_initial", "operand", "result", "v"),
    [
        (0x00, 0x00, 0x00, 0),  # 0 + 0 = 0, smoke test
        (0xc0, 0x80, 0x40, 1),  # -64 + (-128) = 64
        (0xc0, 0xc0, 0x80, 0),  # -64 + (-64) = -128
        (0x80, 0xff, 0x7f, 1),  # -128 + (-1) = 127
        (0x40, 0x01, 0x80, 1),  # 64 + 1 = -128
        (0xff, 0x02, 0x01, 0),  # -1 + 2 = 1
    ],
)
def test_update_overflow_flag(cpu: CPU6502, a_initial: int, operand: int, result: int, v: int):  # noqa: D103
    cpu.update_overflow_flag(a_initial, operand, result)
    assert (cpu.status >> CPU6502.STATUS_V) & 1 == v


def test_clc(cpu: CPU6502):  # noqa: D103
    cpu.status |= 1 << CPU6502.STATUS_C
    assert cpu.status & (1 << CPU6502.STATUS_C) > 0
    cpu.clc()
    assert cpu.status & (1 << CPU6502.STATUS_C) == 0
    assert cpu.cycles == 2  # noqa: PLR2004


def test_sec(cpu: CPU6502):  # noqa: D103
    cpu.status &= ~(1 << CPU6502.STATUS_C)
    assert cpu.status & (1 << CPU6502.STATUS_C) == 0
    cpu.sec()
    assert cpu.status & (1 << CPU6502.STATUS_C) > 0
    assert cpu.cycles == 2  # noqa: PLR2004


def test_cli(cpu: CPU6502):  # noqa: D103
    cpu.status |= 1 << CPU6502.STATUS_I
    assert cpu.status & (1 << CPU6502.STATUS_I) > 0
    cpu.cli()
    assert cpu.status & (1 << CPU6502.STATUS_I) == 0
    assert cpu.cycles == 2  # noqa: PLR2004


def test_sei(cpu: CPU6502):  # noqa: D103
    cpu.status &= ~(1 << CPU6502.STATUS_I)
    assert cpu.status & (1 << CPU6502.STATUS_I) == 0
    cpu.sei()
    assert cpu.status & (1 << CPU6502.STATUS_I) > 0
    assert cpu.cycles == 2  # noqa: PLR2004

def test_cld(cpu: CPU6502):  # noqa: D103
    cpu.status |= 1 << CPU6502.STATUS_D
    assert cpu.status & (1 << CPU6502.STATUS_D) > 0
    cpu.cld()
    assert cpu.status & (1 << CPU6502.STATUS_D) == 0
    assert cpu.cycles == 2  # noqa: PLR2004


def test_sed(cpu: CPU6502):  # noqa: D103
    cpu.status &= ~(1 << CPU6502.STATUS_D)
    assert cpu.status & (1 << CPU6502.STATUS_D) == 0
    cpu.sed()
    assert cpu.status & (1 << CPU6502.STATUS_D) > 0
    assert cpu.cycles == 2  # noqa: PLR2004


def test_clv(cpu: CPU6502):  # noqa: D103
    cpu.status |= 1 << CPU6502.STATUS_V
    assert cpu.status & (1 << CPU6502.STATUS_V) > 0
    cpu.clv()
    assert cpu.status & (1 << CPU6502.STATUS_V) == 0
    assert cpu.cycles == 2  # noqa: PLR2004
