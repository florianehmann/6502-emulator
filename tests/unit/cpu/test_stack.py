"""Test instructions for pushing and pulling from the stack."""


from emulator.cpu import CPU6502
from tests.unit.cpu import (
    TEST_VALUE,
)


def test_pha(cpu: CPU6502):  # noqa: D103
    pha_cycles = 3
    stack_byte_address = cpu.STACK_ROOT + cpu.sp
    cpu.sed()
    cpu.sec()
    cpu.cycles = 0
    old_status = cpu.status
    cpu.a = TEST_VALUE
    cpu.pha()

    assert cpu.memory.read(stack_byte_address) == TEST_VALUE
    assert cpu.cycles == pha_cycles
    assert cpu.status == old_status
