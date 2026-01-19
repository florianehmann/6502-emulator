"""Test CPU."""

import pytest

from emulator.cpu import CPU6502, AddressingMode

ZERO_PAGE_LOCATION: int = 0x20
INDEX: int = 0x05
ABSOLUTE_LOCATION: int = 0x0101  # lower byte + index must be less than 255
PAGE_CROSS_ABSOLUTE_LOCATION: int = 0x0101
PAGE_CROSS_INDEX: int = 0xff

@pytest.mark.parametrize(
    ('mode', 'page_boundary_cross'),
    [
        (AddressingMode.IMMEDIATE, False),
        (AddressingMode.ZERO_PAGE, False),
        (AddressingMode.ZERO_PAGE_X, False),
        (AddressingMode.ABSOLUTE, False),
        (AddressingMode.ABSOLUTE_X, False),
        (AddressingMode.ABSOLUTE_X, True),
    ],
)
def test_lda_addressing(cpu: CPU6502, mode: AddressingMode, page_boundary_cross: bool):  # noqa: D103, FBT001
    test_value = {
        AddressingMode.IMMEDIATE: 0x01,
        AddressingMode.ZERO_PAGE: 0x02,
        AddressingMode.ZERO_PAGE_X: 0x03,
        AddressingMode.ABSOLUTE: 0x04,
        AddressingMode.ABSOLUTE_X: 0x05,
    }
    opcode = {
        AddressingMode.IMMEDIATE: 0xa9,
        AddressingMode.ZERO_PAGE: 0xa5,
        AddressingMode.ZERO_PAGE_X: 0xb5,
        AddressingMode.ABSOLUTE: 0xad,
        AddressingMode.ABSOLUTE_X: 0xbd,
    }
    cycles = {
        AddressingMode.IMMEDIATE: 2,
        AddressingMode.ZERO_PAGE: 3,
        AddressingMode.ZERO_PAGE_X: 4,
        AddressingMode.ABSOLUTE: 4,
        AddressingMode.ABSOLUTE_X: 4,  # no page boundary cross
    }
    pc_after = {
        AddressingMode.IMMEDIATE: 2,
        AddressingMode.ZERO_PAGE: 2,
        AddressingMode.ZERO_PAGE_X: 2,
        AddressingMode.ABSOLUTE: 3,
        AddressingMode.ABSOLUTE_X: 3,
    }
    page_cross_extra_cycles = [AddressingMode.ABSOLUTE_X]

    cpu.pc = 0
    cpu.memory.write(0, opcode[mode])
    match (mode):
        case AddressingMode.IMMEDIATE:
            cpu.memory.write(1, test_value[mode])
        case AddressingMode.ZERO_PAGE:
            cpu.memory.write(1, ZERO_PAGE_LOCATION)
            cpu.memory.write(ZERO_PAGE_LOCATION, test_value[mode])
        case AddressingMode.ZERO_PAGE_X:
            cpu.x = INDEX
            cpu.memory.write(1, ZERO_PAGE_LOCATION)
            cpu.memory.write(ZERO_PAGE_LOCATION + INDEX, test_value[mode])
        case AddressingMode.ABSOLUTE:
            address_lo = ABSOLUTE_LOCATION & 0xff
            address_hi = (ABSOLUTE_LOCATION >> 8) & 0xff
            cpu.memory.write(ABSOLUTE_LOCATION, test_value[mode])
            cpu.memory.write(1, address_lo)
            cpu.memory.write(2, address_hi)
        case AddressingMode.ABSOLUTE_X:
            if page_boundary_cross:
                cpu.x = PAGE_CROSS_INDEX
                absolute_location = PAGE_CROSS_ABSOLUTE_LOCATION
                effective_address = PAGE_CROSS_ABSOLUTE_LOCATION + PAGE_CROSS_INDEX
            else:
                cpu.x = INDEX
                absolute_location = ABSOLUTE_LOCATION
                effective_address = ABSOLUTE_LOCATION + INDEX
            address_lo = absolute_location & 0xff
            address_hi = (absolute_location >> 8) & 0xff
            cpu.memory.write(effective_address, test_value[mode])
            cpu.memory.write(1, address_lo)
            cpu.memory.write(2, address_hi)
        case _:
            raise ValueError
    cpu.step()

    assert cpu.a == test_value[mode]
    assert cpu.cycles == cycles[mode] + (1 if page_boundary_cross and mode in page_cross_extra_cycles else 0)
    assert cpu.pc == pc_after[mode]
