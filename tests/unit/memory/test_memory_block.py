"""Tests for Memory."""

import pytest

from emulator.memory import MemoryBlock


def test_write_bytes(memory: MemoryBlock):  # noqa: D103
    memory.write_bytes(0, bytes([0xab, 0xcd]))
    assert memory.read(0) == 0xab  # noqa: PLR2004
    assert memory.read(1) == 0xcd  # noqa: PLR2004



def test_write_bytes_hex(memory: MemoryBlock):  # noqa: D103
    memory.write_bytes_hex(0, "abcd")
    assert memory.read(0) == 0xab  # noqa: PLR2004
    assert memory.read(1) == 0xcd  # noqa: PLR2004


def test_out_of_bounds_access(memory: MemoryBlock):  # noqa: D103
    with pytest.raises(IndexError, match="out of memory range"):
        memory.read(len(memory.mem))


def test_memory_size():
    """Test if we can read the size of a memory block with the `len` function."""
    mem_size = 1024
    memory = MemoryBlock(mem_size)
    assert len(memory) == mem_size
