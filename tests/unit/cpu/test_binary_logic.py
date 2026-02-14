"""Test instructions for performing binary logic, i.e., BIT, CMP, CPX, CPY."""

import pytest

from emulator.cpu import CPU6502, AddressingMode


@pytest.mark.parametrize(
    ("a", "operand", "n", "z", "v"),
    [
        (0x00, 0x00, 0, 1, 0),
        (0x00, 0x80, 1, 1, 0),
        (0x00, 0x40, 0, 1, 1),
        (0xff, 0xfe, 1, 0, 1),
    ],
    ids=[
        "Smoke test",
        "N flag extraction",
        "V Flag extraction",
        "Mask extraction",
    ],
)
def test_bit_zero_page(cpu: CPU6502, a: int, operand: int, n: int, z: int, v: int):  # noqa: D103, PLR0913
    cpu.a = a
    cpu.memory.write(0x0000, 0x01)
    cpu.memory.write(0x0001, operand)
    cpu.bit(AddressingMode.ZERO_PAGE)

    assert (cpu.status >> CPU6502.STATUS_N) & 1 == n
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == z
    assert (cpu.status >> CPU6502.STATUS_V) & 1 == v
    assert cpu.cycles == CPU6502.BINARY_CYCLE_COUNTS[AddressingMode.ZERO_PAGE]


@pytest.mark.parametrize(
    ("register_value", "operand", "n", "z", "c"),
    [
        (0x00, 0x00, 0, 1, 1),
        (0x00, 0x01, 1, 0, 0),
        (0x01, 0x00, 0, 0, 1),
        (0x01, 0x01, 0, 1, 1),
        (0x7f, 0xff, 1, 0, 0),
        (0x00, 0xff, 0, 0, 0),
    ],
    ids=[
        "Smoke test",
        "Negative flag set",
        "Carry flag set",
        "Zero flag set, carry flag set",
        "Signed overflow",
        "Maximum difference",
    ],
)
def test_compare_logic(cpu: CPU6502, register_value: int, operand: int, n: int, z: int, c: int):  # noqa: D103, PLR0913
    cpu.memory.write(0x0000, operand)
    cpu.compare_logic(register_value, mode=AddressingMode.IMMEDIATE)

    assert (cpu.status >> CPU6502.STATUS_N) & 1 == n
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == z
    assert (cpu.status >> CPU6502.STATUS_C) & 1 == c
