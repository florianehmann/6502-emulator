"""Test CPU."""

import pytest

from emulator.cpu import CPU6502, AddressingMode

ZERO_PAGE_LOCATION: int = 0x20
INDEX: int = 0x05

@pytest.mark.parametrize("mode", [AddressingMode.IMMEDIATE, AddressingMode.ZERO_PAGE, AddressingMode.ZERO_PAGE_X])
def test_lda_addressing(cpu: CPU6502, mode: AddressingMode):  # noqa: D103
    test_value = {
        AddressingMode.IMMEDIATE: 0x01,
        AddressingMode.ZERO_PAGE: 0x02,
        AddressingMode.ZERO_PAGE_X: 0x03,
    }
    opcode = {
        AddressingMode.IMMEDIATE: 0xa9,
        AddressingMode.ZERO_PAGE: 0xa5,
        AddressingMode.ZERO_PAGE_X: 0xb5,
    }
    cycles = {
        AddressingMode.IMMEDIATE: 2,
        AddressingMode.ZERO_PAGE: 3,
        AddressingMode.ZERO_PAGE_X: 4,
    }
    pc_after = {
        AddressingMode.IMMEDIATE: 2,
        AddressingMode.ZERO_PAGE: 2,
        AddressingMode.ZERO_PAGE_X: 2,
    }

    cpu.pc = 0
    cpu.memory.write(0, opcode[mode])
    match (mode):
        case AddressingMode.IMMEDIATE:
            cpu.memory.write(1, test_value[mode])
        case AddressingMode.ZERO_PAGE:
            cpu.memory.write(1, ZERO_PAGE_LOCATION)
            cpu.memory.write(ZERO_PAGE_LOCATION, test_value[mode])
        case AddressingMode.ZERO_PAGE_X:
            cpu.memory.write(1, ZERO_PAGE_LOCATION + INDEX)
            cpu.memory.write(ZERO_PAGE_LOCATION + INDEX, test_value[mode])
        case _:
            raise ValueError
    cpu.step()

    assert cpu.a == test_value[mode]
    assert cpu.cycles == cycles[mode]
    assert cpu.pc == pc_after[mode]
