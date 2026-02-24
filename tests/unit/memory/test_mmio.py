"""Test Memory-Mapped Input/Output functionality."""

import pytest

from emulator.memory import Memory, MemoryMap, MMIORegister

TEST_VALUE = 0xfe


class ReadCountPeripheral:
    """Peripheral with register that returns the number of times it has been read."""

    def __init__(self) -> None:  # noqa: D107
        super().__init__()
        self.value: int = 0
        self.register = MMIORegister(read_callback=self.read, write_callback=self.write)

    def read(self) -> int:  # noqa: D102
        read_count = self.value
        self.value = (self.value + 1) & 0xff
        return read_count

    def write(self, value: int) -> None:  # noqa: D102
        self.value = value & 0xff


mmio_region_n_registers = 2
@pytest.fixture
def mmio_region() -> MemoryMap:
    """Return an MMIOBlock with two `ReadCountRegister` entries at offsets zero and one."""
    mmio_block = MemoryMap()
    for offset in range(mmio_region_n_registers):
        mmio_block.add_block(offset, ReadCountPeripheral().register)
    return mmio_block


def test_mmio_register_reading(mmio_region: Memory):  # noqa: D103
    assert len(mmio_region) == mmio_region_n_registers
    assert mmio_region.read(0) == 0
    assert mmio_region.read(0) == 1
    assert mmio_region.read(1) == 0


def test_mmio_register_writing(mmio_region: Memory):  # noqa: D103
    mmio_region.write(0, TEST_VALUE)
    mmio_region.write(1, 1)
    assert mmio_region.read(0) == TEST_VALUE
    assert mmio_region.read(1) == 1
