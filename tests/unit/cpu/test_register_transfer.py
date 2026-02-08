"""Test instructions for transferring data between registers, i.e., TAX, TAY, etc."""


from emulator.cpu import CPU6502
from tests.unit.cpu import (
    TEST_VALUE,
)


def test_tax(cpu: CPU6502):  # noqa: D103
    cpu.a = TEST_VALUE
    cpu.tax()

    assert cpu.x == TEST_VALUE
    assert cpu.cycles == 2  # noqa: PLR2004
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == 0
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == 1


def test_tay(cpu: CPU6502):  # noqa: D103
    cpu.a = TEST_VALUE
    cpu.tay()

    assert cpu.y == TEST_VALUE
    assert cpu.cycles == 2  # noqa: PLR2004
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == 0
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == 1


def test_tsx(cpu: CPU6502):  # noqa: D103
    cpu.sp = TEST_VALUE
    cpu.tsx()

    assert cpu.x == TEST_VALUE
    assert cpu.cycles == 2  # noqa: PLR2004
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == 0
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == 1


def test_txa(cpu: CPU6502):  # noqa: D103
    cpu.x = TEST_VALUE
    cpu.txa()

    assert cpu.a == TEST_VALUE
    assert cpu.cycles == 2  # noqa: PLR2004
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == 0
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == 1


def test_txs(cpu: CPU6502):  # noqa: D103
    cpu.x = TEST_VALUE
    cpu.txs()

    assert cpu.sp == TEST_VALUE
    assert cpu.cycles == 2  # noqa: PLR2004


def test_tya(cpu: CPU6502):  # noqa: D103
    cpu.y = TEST_VALUE
    cpu.tya()

    assert cpu.a == TEST_VALUE
    assert cpu.cycles == 2  # noqa: PLR2004
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == 0
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == 1
