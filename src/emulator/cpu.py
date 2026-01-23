"""CPU Logic."""

import enum
import logging
from collections.abc import Callable
from functools import partial

from emulator.memory import Memory

logger = logging.getLogger(__name__)


class AddressingMode(enum.Enum):
    """Addressing mode of a 6502 instruction."""

    IMMEDIATE = enum.auto()
    ZERO_PAGE = enum.auto()
    ZERO_PAGE_X = enum.auto()
    ABSOLUTE = enum.auto()
    ABSOLUTE_X = enum.auto()
    ABSOLUTE_Y = enum.auto()
    INDIRECT_X = enum.auto()
    INDIRECT_Y = enum.auto()


class CPU6502:
    """A behavioral model of the MOS6502."""

    def __init__(self, memory: Memory) -> None:
        """Initialize a CPU with memory."""
        # Registers
        self.a:int  = 0
        self.x: int = 0
        self.y: int = 0
        self.pc: int = 0
        self.sp: int = 0xff
        self.status: int = 0
        self.cycles: int = 0

        self.memory = memory
        self.opcodes = self.build_opcode_table()

    def build_opcode_table(self) -> dict[int, Callable[[], None]]:
        """Return a map between opcode and method that contains the logic for the instruction."""
        return {
            0xa1: partial(self.lda, mode=AddressingMode.INDIRECT_X),
            0xa5: partial(self.lda, mode=AddressingMode.ZERO_PAGE),
            0xad: partial(self.lda, mode=AddressingMode.ABSOLUTE),
            0xa9: partial(self.lda, mode=AddressingMode.IMMEDIATE),
            0xb1: partial(self.lda, mode=AddressingMode.INDIRECT_Y),
            0xb5: partial(self.lda, mode=AddressingMode.ZERO_PAGE_X),
            0xb9: partial(self.lda, mode=AddressingMode.ABSOLUTE_Y),
            0xbd: partial(self.lda, mode=AddressingMode.ABSOLUTE_X),
        }

    def step(self) -> None:
        """Step one CPU tick.

        This function executes the next CPU instruction.
        """
        opcode = self.memory.read(self.pc)
        self.pc += 1
        handler = self.opcodes.get(opcode, self.brk)
        handler()

    def brk(self) -> None:
        """Execute BRK instruction."""
        logger.info(f"Unhandled opcode at {self.pc-1:04x}")

    def lda(self, mode: AddressingMode) -> None:
        """Execute LDA instruction with specified addressing mode."""
        match (mode):
            case AddressingMode.IMMEDIATE:
                self.a = self.memory.read(self.pc)
                self.pc += 1
                self.cycles += 2
            case AddressingMode.ZERO_PAGE:
                zero_page_location = self.memory.read(self.pc)
                self.a = self.memory.read(zero_page_location)
                self.pc += 1
                self.cycles += 3
            case AddressingMode.ZERO_PAGE_X:
                zero_page_location = self.memory.read(self.pc)
                self.a = self.memory.read((zero_page_location + self.x) & 0xff)
                self.pc += 1
                self.cycles += 4
            case AddressingMode.ABSOLUTE:
                addr_lo = self.memory.read(self.pc)
                addr_hi = self.memory.read(self.pc + 1)
                addr = (addr_hi << 8) | addr_lo
                self.a = self.memory.read(addr)
                self.pc += 2
                self.cycles += 4
            case AddressingMode.ABSOLUTE_X:
                addr_lo = self.memory.read(self.pc)
                addr_hi = self.memory.read(self.pc + 1)
                addr = (addr_hi << 8) | addr_lo
                self.a = self.memory.read((addr + self.x) & 0xffff)
                self.pc += 2
                self.cycles += 4 if (addr & 0xff00) == ((addr + self.x) & 0xff00) else 5
            case AddressingMode.ABSOLUTE_Y:
                addr_lo = self.memory.read(self.pc)
                addr_hi = self.memory.read(self.pc + 1)
                addr = (addr_hi << 8) | addr_lo
                self.a = self.memory.read((addr + self.y) & 0xffff)
                self.pc += 2
                self.cycles += 4 if (addr & 0xff00) == ((addr + self.y) & 0xff00) else 5
            case AddressingMode.INDIRECT_X:
                addr_zp = (self.memory.read(self.pc) + self.x) & 0xff
                addr_indirect_lo = self.memory.read(addr_zp)
                addr_indirect_hi = self.memory.read((addr_zp + 1) & 0xff)
                addr_indirect = (addr_indirect_hi << 8) | addr_indirect_lo
                self.a = self.memory.read(addr_indirect)
                self.pc += 1
                self.cycles += 6
            case AddressingMode.INDIRECT_Y:
                addr_zp = self.memory.read(self.pc)
                indirect_base_lo = self.memory.read(addr_zp)
                indirect_base_hi = self.memory.read((addr_zp + 1) & 0xff)
                indirect_base = (indirect_base_hi << 8) | indirect_base_lo
                effective_address = (indirect_base + self.y) & 0xffff
                page_boundary_crossed = (indirect_base & 0xff00) != (effective_address & 0xff00)
                self.a = self.memory.read(effective_address)
                self.pc += 1
                self.cycles += 5 if not page_boundary_crossed else 6
            case _:
                # this should not ever be reached when running because the
                # opcode table should never contain an invalid call
                logger.error(f"Invalid addressing mode {mode.name} for LDA instruction.")

        # TODO: Update status register
