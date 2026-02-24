"""Generate a Hello World output message."""  # noqa: INP001

from emulator.cpu import CPU6502, StepResult
from emulator.memory import MemoryBlock, MemoryMap
from emulator.peripherals import TerminalPeripheral

program = bytes.fromhex(
    "a9 41"     # LDA 'A        ; Load character 'A'
    "8d 01 d0"  # STA $D001     ; Store to MMIO for output
    "00",       # BRK
)


if __name__ == "__main__":
    terminal = TerminalPeripheral()
    program_memory = MemoryBlock(0x1000)
    program_memory.write_bytes(0, program)
    system_memory = (
        MemoryMap()
        .add_block(0x0000, MemoryBlock(0x1000))
        .add_block(0x1000, program_memory)
        .add_block(0xd000, terminal.mmio_block)
    )
    system_memory.write(0xd001, 65)
    system_memory.write(0xd001, 66)

    cpu = CPU6502(system_memory)
    cpu.pc = 0x1000
    steps = 0
    while True:
        result = cpu.step()
        steps += 1

        if result == StepResult.BRK:
            break

        if steps > 10:  # noqa: PLR2004
            print("Program didn't halt.")  # noqa: T201

    print()  # noqa: T201

