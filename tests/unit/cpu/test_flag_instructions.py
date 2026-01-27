"""Test instructions that set and store status register flags."""


from emulator.cpu import CPU6502


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
