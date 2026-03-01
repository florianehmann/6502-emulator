"""Test CPU interrupts."""

from emulator.cpu import CPU6502
from emulator.memory import MemoryBlock


def test_irq():  # noqa: D103
    pc_at_irq = 0xa023
    isr_address = 0xe2a4
    interrupt_cycles = 7
    memory = MemoryBlock()
    cpu = CPU6502(memory)
    cpu.pc = pc_at_irq
    cpu.status &= ~(1 << cpu.STATUS_I)  # clear disable flag, allow maskable interrupts
    memory.write(cpu.IRQ_VECTOR, isr_address & 0xff)
    memory.write(cpu.IRQ_VECTOR + 1, (isr_address >> 8) & 0xff)
    old_status = cpu.status
    cpu.irq()

    recovered_status = cpu.pull_byte_from_stack()
    rt_lo = cpu.pull_byte_from_stack()
    rt_hi = cpu.pull_byte_from_stack()
    rt = (rt_hi << 8) | rt_lo

    assert cpu.pc == isr_address
    assert cpu.cycles == interrupt_cycles
    assert rt == pc_at_irq
    assert recovered_status == old_status


def test_irq_with_interrupts_disabled():  # noqa: D103
    pc_at_irq = 0xa023
    isr_address = 0xe2a4
    interrupt_cycles = 0  # IRQ should be ignored when interrupts are disabled
    memory = MemoryBlock()
    cpu = CPU6502(memory)
    cpu.pc = pc_at_irq
    cpu.status |= (1 << cpu.STATUS_I)  # set disable flag, maskable interrupts should be ignored
    memory.write(cpu.IRQ_VECTOR, isr_address & 0xff)
    memory.write(cpu.IRQ_VECTOR + 1, (isr_address >> 8) & 0xff)
    old_status = cpu.status
    cpu.irq()

    assert cpu.pc == pc_at_irq
    assert cpu.cycles == interrupt_cycles
    assert cpu.status == old_status


def test_nmi():  # noqa: D103
    pc_at_nmi = 0xa023
    isr_address = 0xe226
    interrupt_cycles = 7
    memory = MemoryBlock()
    cpu = CPU6502(memory)
    cpu.pc = pc_at_nmi
    cpu.status |= (1 << cpu.STATUS_I)  # set disable flag, maskable interrupts should not affect NMI
    memory.write(cpu.NMI_VECTOR, isr_address & 0xff)
    memory.write(cpu.NMI_VECTOR + 1, (isr_address >> 8) & 0xff)
    old_status = cpu.status
    cpu.nmi()

    recovered_status = cpu.pull_byte_from_stack()
    rt_lo = cpu.pull_byte_from_stack()
    rt_hi = cpu.pull_byte_from_stack()
    rt = (rt_hi << 8) | rt_lo

    assert cpu.pc == isr_address
    assert cpu.cycles == interrupt_cycles
    assert rt == pc_at_nmi
    assert recovered_status == old_status
