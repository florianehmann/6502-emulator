"""Test instructions for performing unary arithmetic, i.e., DEC, INC, etc."""


import pytest

from emulator.cpu import CPU6502, AddressingMode
from tests.unit.cpu import (
    TEST_VALUE,
    ZERO_PAGE_LOCATION,
)


def test_dec(cpu: CPU6502):  # noqa: D103
    cpu.memory.write(0, ZERO_PAGE_LOCATION)
    cpu.memory.write(ZERO_PAGE_LOCATION, TEST_VALUE)
    cpu.dec(AddressingMode.ZERO_PAGE)

    assert cpu.cycles == 5  # noqa: PLR2004
    assert cpu.memory.read(ZERO_PAGE_LOCATION) == TEST_VALUE - 1
    assert cpu.status & (1 << CPU6502.STATUS_N) > 0
    assert cpu.status & (1 << CPU6502.STATUS_Z) == 0


def test_dex(cpu: CPU6502):  # noqa: D103
    cpu.x = TEST_VALUE
    cpu.dex()

    assert cpu.cycles == 2  # noqa: PLR2004
    assert cpu.x == TEST_VALUE - 1
    assert cpu.status & (1 << CPU6502.STATUS_N) > 0
    assert cpu.status & (1 << CPU6502.STATUS_Z) == 0


def test_dey(cpu: CPU6502):  # noqa: D103
    cpu.y = TEST_VALUE
    cpu.dey()

    assert cpu.cycles == 2  # noqa: PLR2004
    assert cpu.y == TEST_VALUE - 1
    assert cpu.status & (1 << CPU6502.STATUS_N) > 0
    assert cpu.status & (1 << CPU6502.STATUS_Z) == 0


def test_inc(cpu: CPU6502):  # noqa: D103
    cpu.memory.write(0, ZERO_PAGE_LOCATION)
    cpu.memory.write(ZERO_PAGE_LOCATION, TEST_VALUE)
    cpu.inc(AddressingMode.ZERO_PAGE)

    assert cpu.cycles == 5  # noqa: PLR2004
    assert cpu.memory.read(ZERO_PAGE_LOCATION) == TEST_VALUE + 1
    assert cpu.status & (1 << CPU6502.STATUS_N) > 0
    assert cpu.status & (1 << CPU6502.STATUS_Z) == 0

def test_inx(cpu: CPU6502):  # noqa: D103
    cpu.x = TEST_VALUE
    cpu.inx()

    assert cpu.cycles == 2  # noqa: PLR2004
    assert cpu.x == TEST_VALUE + 1
    assert cpu.status & (1 << CPU6502.STATUS_N) > 0
    assert cpu.status & (1 << CPU6502.STATUS_Z) == 0


def test_iny(cpu: CPU6502):  # noqa: D103
    cpu.y = TEST_VALUE
    cpu.iny()

    assert cpu.cycles == 2  # noqa: PLR2004
    assert cpu.y == TEST_VALUE + 1
    assert cpu.status & (1 << CPU6502.STATUS_N) > 0
    assert cpu.status & (1 << CPU6502.STATUS_Z) == 0


@pytest.mark.parametrize(("test_value", "c", "z", "n"), [
    (0x80, 1, 1, 0),
    (0x40, 0, 0, 1),
    (0x01, 0, 0, 0),
    (0x41, 0, 0, 1),
    (0x00, 0, 1, 0),
])
def test_asl_accumulator(cpu: CPU6502, test_value: int, c: int, z: int, n: int):  # noqa: D103
    cpu.a = test_value
    cpu.asl(None)

    assert cpu.cycles == 2  # noqa: PLR2004
    assert cpu.a == (test_value << 1) & 0xff
    assert (cpu.status >> CPU6502.STATUS_C) & 1 == c
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == z
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == n


@pytest.mark.parametrize(("test_value", "c", "z"), [
    (0x00, 0, 1),
    (0x01, 1, 1),
    (0x02, 0, 0),
    (0x03, 1, 0),
])
def test_lsr_accumulator(cpu: CPU6502, test_value: int, c: int, z: int):  # noqa: D103
    cpu.a = test_value
    cpu.lsr(None)

    assert cpu.cycles == 2  # noqa: PLR2004
    assert cpu.a == test_value >> 1
    assert (cpu.status >> CPU6502.STATUS_C) & 1 == c
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == z
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == 0
