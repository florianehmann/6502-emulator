"""Test control instructions, i.e., BRK, and NOP."""

from emulator.cpu import CPU6502
from emulator.memory import MemoryBlock


def test_brk():  # noqa: D103
    cpu = CPU6502(MemoryBlock(0x10000))
    cpu.memory.write_bytes_hex(0x0200, "a9 01")  # LDA #$01
    cpu.memory.write_bytes_hex(0x0202, "00")     # BRK
    cpu.a = 1
    cpu.status &= ~(1 << CPU6502.STATUS_Z)
    old_status = cpu.status
    cpu.pc = 0x0203
    cpu.brk()

    assert cpu.pull_byte_from_stack() == old_status | (1 << CPU6502.STATUS_B)
    assert cpu.pull_byte_from_stack() == 0x04  # noqa: PLR2004
    assert cpu.pull_byte_from_stack() == 0x02  # noqa: PLR2004
    assert cpu.cycles == 7  # noqa: PLR2004


def test_jmp_absolute(cpu: CPU6502):  # noqa: D103
    cpu.memory.write_bytes_hex(0, "00 04")
    cpu.jmp(mode="absolute")
    assert cpu.pc == 0x0400  # noqa: PLR2004
    assert cpu.cycles == 3  # noqa: PLR2004


def test_jmp_indirect(cpu: CPU6502):  # noqa: D103
    cpu.memory.write_bytes_hex(0, "00 01")
    cpu.memory.write_bytes_hex(0x0100, "00 02")
    cpu.jmp(mode="indirect")
    assert cpu.pc == 0x0200  # noqa: PLR2004
    assert cpu.cycles == 5  # noqa: PLR2004


def test_jmp_indirect_page_boundary_bug(cpu: CPU6502):
    """Test if the page boundary bug of the original NMOS 6502 is correctly reproduced."""
    cpu.memory.write_bytes_hex(0, "ff 01")
    cpu.memory.write_bytes_hex(0x01ff, "00")
    cpu.memory.write_bytes_hex(0x0100, "02")
    cpu.jmp(mode="indirect")
    assert cpu.pc == 0x0200  # noqa: PLR2004
    assert cpu.cycles == 5  # noqa: PLR2004


def test_jsr(cpu: CPU6502):  # noqa: D103
    jsr_cycle_count = 6
    subroutine_address = 0x0208
    subroutine_address_hi = (subroutine_address >> 8) & 0xff
    subroutine_address_lo = subroutine_address & 0xff
    jsr_last_byte_address = 0x0203
    jsr_last_byte_address_hi = (jsr_last_byte_address >> 8) & 0xff
    jsr_last_byte_address_lo = jsr_last_byte_address & 0xff
    cpu.memory.write_bytes(jsr_last_byte_address - 1, bytes([subroutine_address_lo, subroutine_address_hi]))
    cpu.pc = jsr_last_byte_address - 1
    cpu.jsr()
    assert cpu.pc == subroutine_address
    assert cpu.pull_byte_from_stack() == jsr_last_byte_address_lo
    assert cpu.pull_byte_from_stack() == jsr_last_byte_address_hi
    assert cpu.cycles == jsr_cycle_count


def test_rts(cpu: CPU6502):  # noqa: D103
    rts_cycle_count = 6
    subroutine_address = 0x0208
    jsr_last_byte_address = 0x0203
    jsr_last_byte_address_hi = (jsr_last_byte_address >> 8) & 0xff
    jsr_last_byte_address_lo = jsr_last_byte_address & 0xff
    cpu.push_byte_to_stack(jsr_last_byte_address_hi)
    cpu.push_byte_to_stack(jsr_last_byte_address_lo)
    cpu.pc = subroutine_address + 1  # point to rts opcode
    cpu.rts()
    assert cpu.pc == jsr_last_byte_address + 1
    assert cpu.cycles == rts_cycle_count


def test_nop(cpu: CPU6502):  # noqa: D103
    cpu.nop()
    assert cpu.cycles == 2  # noqa: PLR2004
