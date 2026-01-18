"""Memory for running the CPU."""

class Memory:
    """Simple memory map of contiguous RAM of variable size."""

    def __init__(self, size: int = 65536) -> None:
        """Initialize empty memory of given size.

        Args:
            size: Number of bytes in the memory.

        """
        self.ram = bytearray(size)

    def _check_address_bounds(self, address: int) -> None:
        """Check if memory address is within the bound of this memory."""
        if not (0 <= address < len(self.ram)):
            msg = f"Address {address:04x} out of memory range."
            raise IndexError(msg)

    def read(self, address: int) -> int:
        """Return the byte at the given memory location.

        Args:
            address: Memory location to read byte from.
            value: Value of the byte. Anything below the eight most significant bits is discarded by a bit mask.

        Returns:
            value: Value of byte read from memory.

        Raises:
            IndexError: If address is outside of memory.

        """
        self._check_address_bounds(address)
        return self.ram[address]

    def write(self, address: int, value: int) -> None:
        """Write a value to a memory location.

        Args:
            address: Memory location to write the byte to.
            value: Value of the byte. Anything below the eight most significant bits is discarded by a bit mask.

        Raises:
            IndexError: If address is outside of memory.

        """
        self._check_address_bounds(address)
        self.ram[address] = value & 0xff

    def write_bytes(self, start_address: int, sequence: bytes) -> None:
        """Write a sequence of bytes to a memory region.

        Args:
            start_address: First memory address to be overwritten by `sequence`.
            sequence: Sequence of bytes to write to memory region.

        Raises:
            IndexError: If sequence at specified location exceeds the bounds of the memory.

        """
        self._check_address_bounds(start_address)
        self._check_address_bounds(start_address + len(sequence))
        self.ram[start_address:start_address + len(sequence)] = sequence

    def write_bytes_hex(self, start_address: int, sequence: str) -> None:
        """Write a sequence of bytes written as a string of hexadecimal digits to a memory region.

        Args:
            start_address: First memory address to be overwritten by `sequence`.
            sequence: Sequence of bytes written ad hexadecimal digits to write to memory region.

        Raises:
            IndexError: If sequence at specified location exceeds the bounds of the memory.

        """
        self._check_address_bounds(start_address)
        self._check_address_bounds(start_address + len(sequence))
        self.ram[start_address:start_address + len(sequence)] = bytes.fromhex(sequence)
