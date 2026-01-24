"""Tests for Memory."""

import pytest

from emulator.memory import Memory


def test_write_bytes(memory: Memory):  # noqa: D103
    memory.write_bytes(0, bytes([0xab, 0xcd]))
    assert memory.read(0) == 0xab  # noqa: PLR2004
    assert memory.read(1) == 0xcd  # noqa: PLR2004


def test_write_bytes_hex(memory: Memory):  # noqa: D103
    memory.write_bytes_hex(0, "abcd")
    assert memory.read(0) == 0xab  # noqa: PLR2004
    assert memory.read(1) == 0xcd  # noqa: PLR2004

def test_out_of_bounds_access(memory: Memory):  # noqa: D103
    with pytest.raises(IndexError, match="out of memory range"):
        memory.read(len(memory.ram))
