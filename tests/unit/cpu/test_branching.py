"""Test logic of branching instructions."""

import pytest

from emulator.cpu import CPU6502

TEST_FLAG_OFFSET = 5
N_CYCLES_BRANCH_TAKEN = 3
N_CYCLES_BRANCH_NOT_TAKEN = 2


def test_no_branch_detection(cpu: CPU6502):
    """Test if the branching logic detects when not to branch."""
    cpu.status = 0
    cpu.branch(flag_index=TEST_FLAG_OFFSET, flag_value=1)
    assert cpu.cycles == N_CYCLES_BRANCH_NOT_TAKEN


def test_branch_detection(cpu: CPU6502):
    """Test if the branching logic detects when to branch."""
    cpu.status = 1 << TEST_FLAG_OFFSET
    cpu.branch(flag_index=TEST_FLAG_OFFSET, flag_value=1)
    assert cpu.cycles == N_CYCLES_BRANCH_TAKEN


@pytest.mark.parametrize(
    ("original_pc", "offset", "expected_new_pc"),
    [
        (0x0000, 0x00, 0x0000),
        (0x0000, 0x7f, 0x007f),
        (0x0000, 0x80, 0xff80),
        (0x0001, 0xff, 0x0000),
    ],
    ids=[
        "Branch to next instruction",
        "Branch to instruction 127 bytes ahead",
        "Branch to instruction 128 bytes behind",
        "Branch to instruction 1 byte behind",
    ],
)
def test_branch_offset_calculation(cpu: CPU6502, original_pc: int, offset: int, expected_new_pc: int):
    """Test if the branching logic correctly calculates the new PC."""
    cpu.pc = original_pc
    cpu.memory.write(original_pc, offset)
    cpu.branch(flag_index=TEST_FLAG_OFFSET, flag_value=1)
    assert cpu.pc - 1 == expected_new_pc  # -1 because PC is already advanced after reading the offset



def test_branch_page_boundary_crossing(cpu: CPU6502):
    """Test if the branching logic correctly detects page boundary crossings."""
    instruction_address = 0x00fe
    cpu.status = 1 << TEST_FLAG_OFFSET
    cpu.pc = instruction_address
    cpu.memory.write(instruction_address, 0x01)
    cpu.branch(flag_index=TEST_FLAG_OFFSET, flag_value=1)
    assert cpu.cycles == N_CYCLES_BRANCH_TAKEN + 1
