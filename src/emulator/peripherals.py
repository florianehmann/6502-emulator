"""Collection of common peripherals for emulated systems."""

import sys

from emulator.memory import MemoryMap, MMIORegister


class TerminalPeripheral:
    """Peripheral that allows the emulated system to interact with input and output streams."""

    def __init__(self) -> None:  # noqa: D107
        self.output_register = MMIORegister(write_callback=self.output_character)
        self.mmio_block = (
            MemoryMap()
            .add_block(1, self.output_register)
        )

    def output_character(self, value: int) -> None:
        """Interpret value as ASCII character and print it to stdout."""
        sys.stdout.write(value.to_bytes().decode())
