"""Test control instructions, i.e., BRK, and NOP."""

from emulator.cpu import CPU6502


def test_brk(cpu: CPU6502):  # noqa: D103
    cpu.memory.write_bytes_hex(0x0200, "a9 01")  # LDA #$01
    cpu.memory.write_bytes_hex(0x0202, "00")     # BRK
    cpu.a = 1
    cpu.status &= ~(1 << CPU6502.STATUS_Z)
    cpu.pc = 0x0203
    cpu.brk()

    assert cpu.pull_byte_from_stack() == 0x34  # noqa: PLR2004
    assert cpu.pull_byte_from_stack() == 0x04  # noqa: PLR2004
    assert cpu.pull_byte_from_stack() == 0x02  # noqa: PLR2004
    assert cpu.cycles == 7  # noqa: PLR2004


def test_nop(cpu: CPU6502):  # noqa: D103
    cpu.nop()
    assert cpu.cycles == 2  # noqa: PLR2004
