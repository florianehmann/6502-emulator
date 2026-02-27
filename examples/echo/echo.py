"""Echo typed characters back into stdout."""  # noqa: INP001

import sys
from functools import partial
from pathlib import Path
from queue import Queue
from threading import Thread

from emulator.cpu import CPU6502, run
from emulator.memory import MemoryBlock, MemoryMap
from emulator.peripherals import TerminalPeripheral, monitor_stdin


def handle_inputs(input_queue: Queue[bytes | None]) -> None:
    """Handle incoming bytes from the terminal."""
    if input_queue.qsize() > 0:
        ch = input_queue.get()
        if ch is None:
            sys.exit(0)
        sys.stdout.buffer.write(ch)
        sys.stdout.buffer.flush()


if __name__ == "__main__":
    input_queue = Queue()
    input_handler = partial(handle_inputs, input_queue)
    # Thread(target=monitor_stdin, args=(input_queue,)).start()

    terminal = TerminalPeripheral()
    terminal._input_buffer = 10 # hack additional newline into output

    ram = MemoryBlock(0xD000)
    rom = MemoryBlock(0x2000)
    with (Path(__file__).parent / "6502_code/bin/echo.bin").open("rb") as f:
        rom_contents = f.read()
    for i, b in enumerate(rom_contents):
        rom.write(i, b)
    memory_map = (MemoryMap()
        .add_block(0x0000, ram)
        .add_block(0xD000, terminal.mmio_block)
        .add_block(0xE000, rom))
    cpu = CPU6502(memory_map)
    start_address = (memory_map.read(0xFFFD) << 8) | memory_map.read(0xFFFC)
    cpu.pc = start_address
    run(cpu)

    # while True:
    #     input_handler()
    #     sleep(0.01)
