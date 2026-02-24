"""Tests for Memory Maps."""

from emulator.memory import MemoryBlock, MemoryMap

TEST_VALUE = 0xfe


def test_assemble_single_addresses():  # noqa: D103
    address_0 = MemoryBlock(1)
    address_1 = MemoryBlock(1)
    memory_map = (
        MemoryMap()
        .add_block(0, address_0)
        .add_block(1, address_1)
    )
    assert len(memory_map) == 2  # noqa: PLR2004


def test_read():  # noqa: D103
    page_1 = MemoryBlock(0x0100)
    page_1.write(0x00, TEST_VALUE)
    page_1.write(0xff, TEST_VALUE)
    memory = (
        MemoryMap()
        .add_block(0x0100, page_1)
    )
    assert memory.read(0x0100) == TEST_VALUE
    assert memory.read(0x01ff) == TEST_VALUE
