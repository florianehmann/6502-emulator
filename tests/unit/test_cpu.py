"""Test CPU."""

from emulator.cpu import CPU6502, AddressingMode

ZERO_PAGE_LOCATION = 0x20
INDEX = 0x05
ABSOLUTE_LOCATION = 0x0101  # lower byte + index must be less than 255
PAGE_CROSS_ABSOLUTE_LOCATION = 0x0101
PAGE_CROSS_INDEX = 0xff
ZERO_PAGE_POINTER_LOCATION = 0x08
INDIRECT_DATA_LOCATION_ZERO_PAGE = 0x10
INDIRECT_DATA_LOCATION = 0x0110
TEST_VALUE = 0xfe

# Address resolution


def test_immediate_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.IMMEDIATE)
    assert resolved_address == 1
    assert not page_boundary_crossed


def test_zero_page_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.memory.write(1, ZERO_PAGE_LOCATION)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ZERO_PAGE)
    assert resolved_address == ZERO_PAGE_LOCATION
    assert not page_boundary_crossed


def test_zero_page_x_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.x = INDEX
    cpu.memory.write(1, ZERO_PAGE_LOCATION)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ZERO_PAGE_X)
    assert resolved_address == ZERO_PAGE_LOCATION + INDEX
    assert not page_boundary_crossed


def test_zero_page_y_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = INDEX
    cpu.memory.write(1, ZERO_PAGE_LOCATION)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ZERO_PAGE_Y)
    assert resolved_address == ZERO_PAGE_LOCATION + INDEX
    assert not page_boundary_crossed


def test_absolute_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE)
    assert resolved_address == ABSOLUTE_LOCATION
    assert not page_boundary_crossed


def test_absolute_x_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.x = INDEX
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE_X)
    assert resolved_address == ABSOLUTE_LOCATION + INDEX
    assert not page_boundary_crossed


def test_absolute_x_addressing_with_page_cross(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.x = PAGE_CROSS_INDEX
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE_X)
    assert resolved_address == ABSOLUTE_LOCATION + PAGE_CROSS_INDEX
    assert page_boundary_crossed


def test_absolute_y_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = INDEX
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE_Y)
    assert resolved_address == ABSOLUTE_LOCATION + INDEX
    assert not page_boundary_crossed


def test_absolute_y_addressing_with_page_cross(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = PAGE_CROSS_INDEX
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE_Y)
    assert resolved_address == ABSOLUTE_LOCATION + PAGE_CROSS_INDEX
    assert page_boundary_crossed


def test_indirect_x_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.x = INDEX
    cpu.memory.write(1, ZERO_PAGE_POINTER_LOCATION)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION + INDEX, INDIRECT_DATA_LOCATION_ZERO_PAGE)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.INDIRECT_X)
    assert resolved_address == INDIRECT_DATA_LOCATION_ZERO_PAGE
    assert not page_boundary_crossed


def test_indirect_y_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = INDEX
    cpu.memory.write(1, ZERO_PAGE_POINTER_LOCATION)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION, INDIRECT_DATA_LOCATION & 0xff)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION + 1, (INDIRECT_DATA_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.INDIRECT_Y)
    assert resolved_address == INDIRECT_DATA_LOCATION + INDEX
    assert not page_boundary_crossed


def test_indirect_y_addressing_with_page_cross(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = PAGE_CROSS_INDEX
    cpu.memory.write(1, ZERO_PAGE_POINTER_LOCATION)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION, INDIRECT_DATA_LOCATION & 0xff)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION + 1, (INDIRECT_DATA_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.INDIRECT_Y)
    assert resolved_address == INDIRECT_DATA_LOCATION + PAGE_CROSS_INDEX
    assert page_boundary_crossed


# Flag instructions


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


# Register loading


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


# Register storing


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
