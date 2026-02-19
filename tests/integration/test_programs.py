"""Test simple 6502 machine code to exercise instructions in combination."""

import pytest

from emulator.cpu import CPU6502, StepResult


def test_minimal_program(cpu: CPU6502):
    """Test basic program execution functionality."""
    cpu.memory.write_bytes_hex(0x200,
        "a9 01"     # LDA #$01
        "8d 00 02"  # STA $0200
        "a9 05"     # LDA #$05
        "8d 01 02"  # STA $0201
        "00",       # BRK
    )
    cpu.pc = 0x200
    steps = 0
    while True:
        result = cpu.step()
        steps += 1

        if result == StepResult.BRK:
            break

        if steps > 10:  # noqa: PLR2004
            pytest.fail("Program didn't halt.")

    assert cpu.a == 5  # noqa: PLR2004
    assert cpu.memory.read(0x0200) == 1
    assert cpu.memory.read(0x0201) == 5  # noqa: PLR2004
    assert cpu.cycles == 19  # noqa: PLR2004


def test_loop_program(cpu: CPU6502):
    """Test looping."""
    cpu.memory.write_bytes_hex(0x300,
        "a2 05"     # LDX #$05
        "a9 00"     # LDY #$00
        "18"        # loop: CLC
        "69 01"     # ADC #$01
        "ca"        # DEX
        "d0 fa"     # BNE loop
        "8d 00 02"  # STA $0200
        "00",       # BRK
    )
    cpu.pc = 0x0300
    steps = 0
    while True:
        result = cpu.step()
        steps += 1

        if result == StepResult.BRK:
            break

        if steps > 300:  # noqa: PLR2004
            pytest.fail("Program didn't halt.")

    assert cpu.cycles == 59  # noqa: PLR2004
    assert cpu.memory.read(0x0200) == 0x05  # noqa: PLR2004


def test_subroutine_program(cpu: CPU6502):
    """Test if jumping to and returning from subroutines works."""
    cpu.memory.write_bytes_hex(0x300,
                    # * = $0300
        "a9 05"     #       LDA #$05
        "20 09 03"  #       JSR DECA
        "18"        #       CLC
        "69 02"     #       ADC #$02
        "00"        #       BRK
        "38"        # DECA: SEC
        "e9 01"     #       SBC #$01
        "60",       #       RTS
    )
    cpu.pc = 0x0300
    steps = 0
    while True:
        result = cpu.step()
        steps += 1

        if result == StepResult.BRK:
            break

        if steps > 10:  # noqa: PLR2004
            pytest.fail("Program didn't halt.")

    assert cpu.cycles == 29  # noqa: PLR2004
    assert cpu.a == 6  # noqa: PLR2004
