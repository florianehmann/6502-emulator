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


def test_php(cpu: CPU6502):  # noqa: D103
    php_cycles = 3
    cpu.sed()
    cpu.sec()
    status = cpu.status
    cpu.cycles = 0
    cpu.php()

    assert cpu.pull_byte_from_stack() == status | (1 << CPU6502.STATUS_B)
    assert cpu.cycles == php_cycles


def test_pla(cpu: CPU6502):  # noqa: D103
    pla_cycles = 4
    cpu.push_byte_to_stack(TEST_VALUE)
    cpu.pla()

    assert cpu.a == TEST_VALUE
    assert cpu.cycles == pla_cycles
    assert (cpu.status >> CPU6502.STATUS_N) & 1 > 0
    assert (cpu.status >> CPU6502.STATUS_Z) & 1 == 0


def test_plp(cpu: CPU6502):  # noqa: D103
    plp_cycles = 4
    old_status = cpu.status
    status_to_push = old_status | (1 << CPU6502.STATUS_B)
    cpu.push_byte_to_stack(status_to_push)
    cpu.plp()

    assert cpu.status == old_status & ~(1 << CPU6502.STATUS_B)
    assert cpu.cycles == plp_cycles
