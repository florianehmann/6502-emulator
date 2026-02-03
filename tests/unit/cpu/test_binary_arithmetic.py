"""Test instructions for performing binary arithmetic, i.e., ADC, SBC, AND, ORA, etc."""

import pytest

from emulator.cpu import CPU6502, AddressingMode
from emulator.utils import dec_to_bcd


@pytest.mark.parametrize(
    ("a_initial", "operand", "c_in", "a", "c", "v", "z", "n"),
    [
        (0x00, 0x00, 0, 0x00, 0, 0, 1, 0),
        (0xc0, 0x80, 0, 0x40, 1, 1, 0, 0),
        (0xc0, 0xc0, 0, 0x80, 1, 0, 0, 1),  # Overflows in unsigned interpretation -> Carry set
        (0x80, 0xff, 0, 0x7f, 1, 1, 0, 0),  # Overflows in unsigned interpretation -> Carry set
        (0xff, 0x02, 0, 0x01, 1, 0, 0, 0),  # Overflows in unsigned interpretation -> Carry set
    ],
    ids=[
        "0 + 0 = 0, Smoke test",
        "-64 + (-128) = 64",
        "-64 + (-64) = -128",
        "-128 + (-1) = -127",
        "-1 + 2 = 1",
    ],
)
def test_adc(cpu: CPU6502, a_initial: int, operand: int, c_in: int, a: int, c: int, v: int, z: int, n: int):  # noqa: D103, PLR0913
    cpu.a = a_initial
    cpu.status &= ~(1 << CPU6502.STATUS_C)
    cpu.status |= c_in << CPU6502.STATUS_C
    cpu.memory.write(0, operand)
    cpu.adc(AddressingMode.IMMEDIATE)

    assert cpu.a == a
    assert (cpu.status >> CPU6502.STATUS_C) & 1 == c
    assert (cpu.status >> CPU6502.STATUS_V) & 1 == v
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == z
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == n
    assert cpu.cycles == 2  # noqa: PLR2004


@pytest.mark.parametrize(
    ("a_initial", "operand", "c_in", "a", "c", "v", "z", "n"),
    [
        (dec_to_bcd(0),  dec_to_bcd(0), 0, dec_to_bcd(0),  0, 0, 1, 0),
        (dec_to_bcd(0),  dec_to_bcd(1), 0, dec_to_bcd(1),  0, 0, 0, 0),
        (dec_to_bcd(9),  dec_to_bcd(1), 0, dec_to_bcd(10), 0, 0, 0, 0),
        (dec_to_bcd(10), dec_to_bcd(1), 0, dec_to_bcd(11), 0, 0, 0, 0),
        (dec_to_bcd(99), dec_to_bcd(1), 0, dec_to_bcd(0),  1, 0, 0, 1),
        (dec_to_bcd(5),  dec_to_bcd(5), 0, dec_to_bcd(10), 0, 0, 0, 0),
        (dec_to_bcd(9),  dec_to_bcd(9), 0, dec_to_bcd(18), 0, 0, 0, 0),
        (dec_to_bcd(99), dec_to_bcd(1), 1, dec_to_bcd(1),  1, 0, 0, 1),
        (dec_to_bcd(49), dec_to_bcd(1), 0, dec_to_bcd(50), 0, 0, 0, 0),
        (dec_to_bcd(89), dec_to_bcd(9), 1, dec_to_bcd(99), 0, 0, 0, 1),
    ],
    ids=[
        "0 + 0 = 0, Smoke test",
        "0 + 1 = 1",
        "9 + 1 = 10",
        "10 + 1 = 11",
        "99 + 1 = 0, Carry set, Negative flag weirdness",
        "5 + 5 = 10, Nibble carry",
        "9 + 9 = 18, Both nibbles >= 9",
        "99 + 1 + carry = 1",
        "49 + 1 = 50, Low nibble carry only",
        "89 + 9 + carry = 99, Negative flag weirdness",
    ],
)
def test_adc_decimal(cpu: CPU6502, a_initial: int, operand: int, c_in: int, a: int, c: int, v: int, z: int, n: int):  # noqa: D103, PLR0913
    cpu.a = a_initial
    cpu.status |= (1 << CPU6502.STATUS_D)
    cpu.status &= ~(1 << CPU6502.STATUS_C)
    cpu.status |= c_in << CPU6502.STATUS_C
    cpu.memory.write(0, operand)
    cpu.adc(AddressingMode.IMMEDIATE)

    assert cpu.a == a
    assert (cpu.status >> CPU6502.STATUS_C) & 1 == c
    assert (cpu.status >> CPU6502.STATUS_V) & 1 == v
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == z
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == n
    assert cpu.cycles == 2  # noqa: PLR2004


@pytest.mark.parametrize(
    ("a_initial", "operand", "a", "z", "n"),
    [
        (0x00, 0x00, 0x00, 1, 0),
        (0xff, 0x0f, 0x0f, 0, 0),
        (0xff, 0xf0, 0xf0, 0, 1),
    ],
    ids=[
        "0x00 & 0x00 = 0, Smoke test",
        "0xff & 0x0f = 0x0f",
        "0xff & 0xf0 = 0xf0",
    ],
)
def test_and_op(cpu: CPU6502, a_initial: int, operand: int, a: int, z: int, n: int):  # noqa: D103, PLR0913
    cpu.a = a_initial
    cpu.memory.write(0, operand)
    cpu.and_op(AddressingMode.IMMEDIATE)

    assert cpu.a == a
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == z
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == n
    assert cpu.cycles == 2  # noqa: PLR2004


@pytest.mark.parametrize(
    ("a_initial", "operand", "c_in", "a", "c", "v", "z", "n"),
    [
        (0x00, 0x00, 1, 0x00, 1, 0, 1, 0),
        (0x05, 0x05, 1, 0x00, 1, 0, 1, 0),
        (0x05, 0x05, 0, 0xff, 0, 0, 0, 1),
        (0x80, 0x01, 1, 0x7f, 1, 1, 0, 0),
        (0x7f, 0xff, 1, 0x80, 0, 1, 0, 1),
    ],
    ids=[
        "0 - 0 = 0, Smoke test",
        "5 - 5 = 0",
        "5 - 5 - 1 = -1",
        "-128 - 1 = 126",
        "127 - (-1) = -128",
    ],
)
def test_sbc(cpu: CPU6502, a_initial: int, operand: int, c_in: int, a: int, c: int, v: int, z: int, n: int):  # noqa: D103, PLR0913
    cpu.a = a_initial
    cpu.status &= ~(1 << CPU6502.STATUS_C)
    cpu.status |= c_in << CPU6502.STATUS_C
    cpu.memory.write(0, operand)
    cpu.sbc(AddressingMode.IMMEDIATE)

    assert cpu.a == a
    assert (cpu.status >> CPU6502.STATUS_C) & 1 == c
    assert (cpu.status >> CPU6502.STATUS_V) & 1 == v
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == z
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == n
    assert cpu.cycles == 2  # noqa: PLR2004


@pytest.mark.parametrize(
    ("a_initial", "operand", "c_in", "a", "c", "v", "z", "n"),
    [
        (dec_to_bcd(0),  dec_to_bcd(0),  1, dec_to_bcd(0),  1, 0, 1, 0),
        (dec_to_bcd(5),  dec_to_bcd(5),  1, dec_to_bcd(0),  1, 0, 1, 0),
        (dec_to_bcd(5),  dec_to_bcd(5),  0, dec_to_bcd(99), 0, 0, 0, 1),
        (dec_to_bcd(80), dec_to_bcd(1),  1, dec_to_bcd(79), 1, 1, 0, 0),
        (dec_to_bcd(1),  dec_to_bcd(99), 1, dec_to_bcd(2),  0, 0, 0, 0),
        (dec_to_bcd(10), dec_to_bcd(1),  1, dec_to_bcd(9),  1, 0, 0, 0),
        (dec_to_bcd(20), dec_to_bcd(1),  0, dec_to_bcd(18), 1, 0, 0, 0),
        (dec_to_bcd(20), dec_to_bcd(1),  1, dec_to_bcd(19), 1, 0, 0, 0),
    ],
    ids=[
        "0 - 0 = 0, Smoke test",
        "5 - 5 = 0",
        "5 - 5 - 1 = 99",
        "80 - 1 = 79, Negative flag weirdness",
        "1 - 99 = 2",
        "10 - 1 = 9",
        "20 - 1 - 1 = 18, Decade transition with borrow",
        "20 - 1 = 20, Decade transition",
    ],
)
def test_sbc_decimal(cpu: CPU6502, a_initial: int, operand: int, c_in: int, a: int, c: int, v: int, z: int, n: int):  # noqa: D103, PLR0913
    cpu.a = a_initial
    cpu.status |= (1 << CPU6502.STATUS_D)
    cpu.status &= ~(1 << CPU6502.STATUS_C)
    cpu.status |= c_in << CPU6502.STATUS_C
    cpu.memory.write(0, operand)
    cpu.sbc(AddressingMode.IMMEDIATE)

    assert cpu.a == a
    assert (cpu.status >> CPU6502.STATUS_C) & 1 == c
    assert (cpu.status >> CPU6502.STATUS_V) & 1 == v
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == z
    assert (cpu.status >> CPU6502.STATUS_N) & 1 == n
    assert cpu.cycles == 2  # noqa: PLR2004
