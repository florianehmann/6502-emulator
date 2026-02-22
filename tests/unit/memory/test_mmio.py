"""Test Memory-Mapped Input/Output functionality."""

from typing import override

import pytest

from emulator.memory import MMIOBlock, MMIOHandler

TEST_VALUE = 0xfe


class ReadCountRegister(MMIOHandler):
    """Register that returns the number of times it has been read."""

    def __init__(self) -> None:  # noqa: D107
        super().__init__()
        self.value: int = 0

    @override
    def read(self) -> int:
        read_count = self.value
        self.value = (self.value + 1) & 0xff
        return read_count

    @override
    def write(self, value: int) -> None:
        self.value = value & 0xff


mmio_region_n_registers = 2
@pytest.fixture
def mmio_region() -> MMIOBlock:
    """Return an MMIOBlock with two `ReadCountRegister` entries at offsets zero and one."""
    mmio_block = MMIOBlock()
    for offset in range(mmio_region_n_registers):
        mmio_block.add_register(offset, ReadCountRegister())
    return mmio_block


def test_mmio_register_reading(mmio_region: MMIOBlock):  # noqa: D103
    assert len(mmio_region) == mmio_region_n_registers
    assert mmio_region.read(0) == 0
    assert mmio_region.read(0) == 1
    assert mmio_region.read(1) == 0


def test_mmio_register_writing(mmio_region: MMIOBlock):  # noqa: D103
    mmio_region.write(0, TEST_VALUE)
    mmio_region.write(1, 1)
    assert mmio_region.read(0) == TEST_VALUE
    assert mmio_region.read(1) == 1
