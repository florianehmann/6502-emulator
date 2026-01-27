"""Test memory address resolution for the different addressing modes."""

from emulator.cpu import CPU6502, AddressingMode
from tests.unit.cpu import (
    ABSOLUTE_LOCATION,
    INDEX,
    INDIRECT_DATA_LOCATION,
    INDIRECT_DATA_LOCATION_ZERO_PAGE,
    PAGE_CROSS_INDEX,
    ZERO_PAGE_LOCATION,
    ZERO_PAGE_POINTER_LOCATION,
)


def test_immediate_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.IMMEDIATE)
    assert resolved_address == 1
    assert not page_boundary_crossed


def test_zero_page_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.memory.write(1, ZERO_PAGE_LOCATION)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ZERO_PAGE)
    assert resolved_address == ZERO_PAGE_LOCATION
    assert not page_boundary_crossed


def test_zero_page_x_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.x = INDEX
    cpu.memory.write(1, ZERO_PAGE_LOCATION)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ZERO_PAGE_X)
    assert resolved_address == ZERO_PAGE_LOCATION + INDEX
    assert not page_boundary_crossed


def test_zero_page_y_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = INDEX
    cpu.memory.write(1, ZERO_PAGE_LOCATION)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ZERO_PAGE_Y)
    assert resolved_address == ZERO_PAGE_LOCATION + INDEX
    assert not page_boundary_crossed


def test_absolute_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE)
    assert resolved_address == ABSOLUTE_LOCATION
    assert not page_boundary_crossed


def test_absolute_x_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.x = INDEX
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE_X)
    assert resolved_address == ABSOLUTE_LOCATION + INDEX
    assert not page_boundary_crossed


def test_absolute_x_addressing_with_page_cross(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.x = PAGE_CROSS_INDEX
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE_X)
    assert resolved_address == ABSOLUTE_LOCATION + PAGE_CROSS_INDEX
    assert page_boundary_crossed


def test_absolute_y_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = INDEX
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE_Y)
    assert resolved_address == ABSOLUTE_LOCATION + INDEX
    assert not page_boundary_crossed


def test_absolute_y_addressing_with_page_cross(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = PAGE_CROSS_INDEX
    cpu.memory.write(1, ABSOLUTE_LOCATION & 0xff)
    cpu.memory.write(2, (ABSOLUTE_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.ABSOLUTE_Y)
    assert resolved_address == ABSOLUTE_LOCATION + PAGE_CROSS_INDEX
    assert page_boundary_crossed


def test_indirect_x_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.x = INDEX
    cpu.memory.write(1, ZERO_PAGE_POINTER_LOCATION)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION + INDEX, INDIRECT_DATA_LOCATION_ZERO_PAGE)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.INDIRECT_X)
    assert resolved_address == INDIRECT_DATA_LOCATION_ZERO_PAGE
    assert not page_boundary_crossed


def test_indirect_y_addressing(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = INDEX
    cpu.memory.write(1, ZERO_PAGE_POINTER_LOCATION)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION, INDIRECT_DATA_LOCATION & 0xff)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION + 1, (INDIRECT_DATA_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.INDIRECT_Y)
    assert resolved_address == INDIRECT_DATA_LOCATION + INDEX
    assert not page_boundary_crossed


def test_indirect_y_addressing_with_page_cross(cpu: CPU6502):  # noqa: D103
    cpu.pc = 1
    cpu.y = PAGE_CROSS_INDEX
    cpu.memory.write(1, ZERO_PAGE_POINTER_LOCATION)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION, INDIRECT_DATA_LOCATION & 0xff)
    cpu.memory.write(ZERO_PAGE_POINTER_LOCATION + 1, (INDIRECT_DATA_LOCATION >> 8) & 0xff)
    resolved_address, page_boundary_crossed = cpu.resolve_address(AddressingMode.INDIRECT_Y)
    assert resolved_address == INDIRECT_DATA_LOCATION + PAGE_CROSS_INDEX
    assert page_boundary_crossed
