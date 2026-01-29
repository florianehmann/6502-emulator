"""Test instructions for performing unary arithmetic, i.e., DEC, INC, etc."""


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
