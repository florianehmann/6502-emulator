"""Test register storing instructions, i.e., STA, STX, and STY."""

from emulator.cpu import CPU6502, AddressingMode
from tests.unit.cpu import ABSOLUTE_LOCATION, PAGE_CROSS_INDEX, TEST_VALUE


def test_sta_absolute_x(cpu: CPU6502):  # noqa: D103
    effective_addr = ABSOLUTE_LOCATION + PAGE_CROSS_INDEX
    addr_lo = ABSOLUTE_LOCATION & 0xff
    addr_hi = (ABSOLUTE_LOCATION >> 8) & 0xff
    cpu.memory.write(0, addr_lo)
    cpu.memory.write(1, addr_hi)
    cpu.a = TEST_VALUE
    cpu.x = PAGE_CROSS_INDEX
    cpu.sta(AddressingMode.ABSOLUTE_X)

    assert cpu.memory.read(effective_addr) == TEST_VALUE
    assert cpu.cycles == 5  # noqa: PLR2004
    assert cpu.pc == 2  # noqa: PLR2004


def test_stx_absolute(cpu: CPU6502):  # noqa: D103
    addr_lo = ABSOLUTE_LOCATION & 0xff
    addr_hi = (ABSOLUTE_LOCATION >> 8) & 0xff
    cpu.memory.write(0, addr_lo)
    cpu.memory.write(1, addr_hi)
    cpu.x = TEST_VALUE
    cpu.stx(AddressingMode.ABSOLUTE)

    assert cpu.memory.read(ABSOLUTE_LOCATION) == TEST_VALUE
    assert cpu.cycles == 4  # noqa: PLR2004
    assert cpu.pc == 2  # noqa: PLR2004


def test_sty_absolute(cpu: CPU6502):  # noqa: D103
    addr_lo = ABSOLUTE_LOCATION & 0xff
    addr_hi = (ABSOLUTE_LOCATION >> 8) & 0xff
    cpu.memory.write(0, addr_lo)
    cpu.memory.write(1, addr_hi)
    cpu.y = TEST_VALUE
    cpu.sty(AddressingMode.ABSOLUTE)

    assert cpu.memory.read(ABSOLUTE_LOCATION) == TEST_VALUE
    assert cpu.cycles == 4  # noqa: PLR2004
    assert cpu.pc == 2  # noqa: PLR2004
