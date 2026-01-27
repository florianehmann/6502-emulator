"""Test instructions for loading data from memories into registers, i.e., LDA, LDX, and LDY."""


from emulator.cpu import CPU6502, AddressingMode
from tests.unit.cpu import (
    ABSOLUTE_LOCATION,
    PAGE_CROSS_INDEX,
    TEST_VALUE,
)


def test_lda_absolute_x(cpu: CPU6502):  # noqa: D103
    cpu.memory.write(0, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(1, (ABSOLUTE_LOCATION >> 8) & 0xff)
    cpu.memory.write(ABSOLUTE_LOCATION + PAGE_CROSS_INDEX, TEST_VALUE)
    cpu.x = PAGE_CROSS_INDEX
    cpu.lda(AddressingMode.ABSOLUTE_X)

    assert cpu.a == TEST_VALUE
    assert cpu.cycles == 5  # noqa: PLR2004


def test_ldx_absolute_y(cpu: CPU6502):  # noqa: D103
    cpu.memory.write(0, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(1, (ABSOLUTE_LOCATION >> 8) & 0xff)
    cpu.memory.write(ABSOLUTE_LOCATION + PAGE_CROSS_INDEX, TEST_VALUE)
    cpu.y = PAGE_CROSS_INDEX
    cpu.ldx(AddressingMode.ABSOLUTE_Y)

    assert cpu.x == TEST_VALUE
    assert cpu.cycles == 5  # noqa: PLR2004


def test_ldy_absolute_x(cpu: CPU6502):  # noqa: D103
    cpu.memory.write(0, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(1, (ABSOLUTE_LOCATION >> 8) & 0xff)
    cpu.memory.write(ABSOLUTE_LOCATION + PAGE_CROSS_INDEX, TEST_VALUE)
    cpu.x = PAGE_CROSS_INDEX
    cpu.ldy(AddressingMode.ABSOLUTE_X)

    assert cpu.y == TEST_VALUE
    assert cpu.cycles == 5  # noqa: PLR2004
