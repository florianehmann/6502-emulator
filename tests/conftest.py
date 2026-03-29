"""Fixtures for testing."""

import pytest

from another6502.cpu import CPU6502
from another6502.memory import Memory, MemoryBlock


@pytest.fixture
def memory() -> Memory:
    """Return 1K of RAM initialized to zero."""
    return MemoryBlock(1024)


@pytest.fixture
def cpu(memory: Memory) -> CPU6502:
    """Return a CPU with 1K of RAM initialized to zero and PC at zero."""
    return CPU6502(memory, override_initial_pc=0)
