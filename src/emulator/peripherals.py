"""Collection of common peripherals for emulated systems."""

import sys
import termios
import tty
from queue import Queue
from typing import ClassVar

from emulator.memory import MemoryMap, MMIORegister


class TerminalPeripheral:
    """Peripheral that allows the emulated system to interact with input and output streams."""

    STATUS_WAITING: ClassVar[int] = 7

    def __init__(self) -> None:
        """Initialize MMIO registers and build memory map.

        After initialization, the peripheral can be used by reading from and writing to the registers in `mmio_block`.
        """
        self._input_buffer: int = 0
        self._input_buffer_waiting: bool = True
        self._status_register = MMIORegister(read_callback=self._status)
        self._output_register = MMIORegister(write_callback=self._output_character)
        self._input_register = MMIORegister(read_callback=self._input_character)
        self.mmio_block = (MemoryMap()
            .add_block(0, self._status_register)
            .add_block(1, self._output_register)
            .add_block(2, self._input_register))

    def _status(self) -> int:
        status = 0
        status |= (self._input_buffer_waiting << self.STATUS_WAITING)
        return status

    def _output_character(self, value: int) -> None:
        """Interpret value as ASCII character and print it to stdout."""
        sys.stdout.write(value.to_bytes().decode())

    def _input_character(self) -> int:
        self._input_buffer_waiting = False
        return self._input_buffer & 0xff


def monitor_stdin(input_queue: Queue[bytes | None]) -> None:
    """Set terminal to raw mode and put incoming bytes on stdin into a queue.

    When this function receives a Ctrl+C (0x03) or encounters an exception, it restores the terminal to its
    previous state.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.buffer.read(1)
            if ch == b"\x03":  # Ctrl+C / End of Text
                input_queue.put(None)
                return
            input_queue.put(ch)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
