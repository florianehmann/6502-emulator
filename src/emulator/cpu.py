"""CPU Logic."""

import enum
import logging
from collections.abc import Callable
from functools import partial

from emulator.memory import Memory
from emulator.utils import assert_never

logger = logging.getLogger(__name__)


class AddressingMode(enum.Enum):
    """Addressing mode of a 6502 instruction."""

    IMMEDIATE = enum.auto()
    ZERO_PAGE = enum.auto()
    ZERO_PAGE_X = enum.auto()
    ZERO_PAGE_Y = enum.auto()
    ABSOLUTE = enum.auto()
    ABSOLUTE_X = enum.auto()
    ABSOLUTE_Y = enum.auto()
    INDIRECT_X = enum.auto()
    INDIRECT_Y = enum.auto()


class StepResult(enum.Enum):
    """Result of a CPU fetch/execute step."""

    NORMAL = enum.auto()
    BRK = enum.auto()


class CPU6502:
    """A behavioral model of the MOS6502."""

    STATUS_C = 0
    STATUS_Z = 1
    STATUS_I = 2
    STATUS_D = 3
    STATUS_B = 4
    STATUS_V = 6
    STATUS_N = 7

    STACK_ROOT = 0x0100

    def __init__(self, memory: Memory) -> None:
        """Initialize a CPU with memory."""
        # Registers
        self.a: int = 0
        self.x: int = 0
        self.y: int = 0
        self.pc: int = 0
        self.sp: int = 0xff
        self.status: int = 0
        self.cycles: int = 0

        self.memory = memory
        self.opcodes = self.build_opcode_table()

        # initial values for the status register
        self.status |= (1 << self.STATUS_Z)
        self.status |= (1 << self.STATUS_I)
        self.status |= (1 << 5)  # unused bit of the status register is usually set

    def build_opcode_table(self) -> dict[int, Callable[[], None]]:
        """Return a map between opcode and method that contains the logic for the instruction."""
        return {
            0x00: self.brk,
            0x18: self.clc,
            0x38: self.sec,
            0x58: self.cli,
            0x78: self.sei,
            0x81: partial(self.sta, mode=AddressingMode.INDIRECT_X),
            0x85: partial(self.sta, mode=AddressingMode.ZERO_PAGE),
            0x86: partial(self.stx, mode=AddressingMode.ZERO_PAGE),
            0x8d: partial(self.sta, mode=AddressingMode.ABSOLUTE),
            0x8e: partial(self.stx, mode=AddressingMode.ABSOLUTE),
            0x91: partial(self.sta, mode=AddressingMode.INDIRECT_Y),
            0x95: partial(self.sta, mode=AddressingMode.ZERO_PAGE_X),
            0x96: partial(self.stx, mode=AddressingMode.ZERO_PAGE_Y),
            0x99: partial(self.sta, mode=AddressingMode.ABSOLUTE_Y),
            0x9d: partial(self.sta, mode=AddressingMode.ABSOLUTE_X),
            0xa0: partial(self.ldy, mode=AddressingMode.IMMEDIATE),
            0xa1: partial(self.lda, mode=AddressingMode.INDIRECT_X),
            0xa2: partial(self.ldx, mode=AddressingMode.IMMEDIATE),
            0xa4: partial(self.ldy, mode=AddressingMode.ZERO_PAGE),
            0xa5: partial(self.lda, mode=AddressingMode.ZERO_PAGE),
            0xa6: partial(self.ldx, mode=AddressingMode.ZERO_PAGE),
            0xa9: partial(self.lda, mode=AddressingMode.IMMEDIATE),
            0xac: partial(self.ldy, mode=AddressingMode.ABSOLUTE),
            0xad: partial(self.lda, mode=AddressingMode.ABSOLUTE),
            0xae: partial(self.ldx, mode=AddressingMode.ABSOLUTE),
            0xb1: partial(self.lda, mode=AddressingMode.INDIRECT_Y),
            0xb4: partial(self.ldy, mode=AddressingMode.ZERO_PAGE_X),
            0xb5: partial(self.lda, mode=AddressingMode.ZERO_PAGE_X),
            0xb6: partial(self.ldx, mode=AddressingMode.ZERO_PAGE_Y),
            0xb8: self.clv,
            0xb9: partial(self.lda, mode=AddressingMode.ABSOLUTE_Y),
            0xbc: partial(self.ldy, mode=AddressingMode.ABSOLUTE_X),
            0xbd: partial(self.lda, mode=AddressingMode.ABSOLUTE_X),
            0xbe: partial(self.ldx, mode=AddressingMode.ABSOLUTE_Y),
            0xd8: self.cld,
            0xf8: self.sed,
        }

    def step(self) -> StepResult:
        """Step one CPU tick.

        This function executes the next CPU instruction.
        """
        opcode = self.memory.read(self.pc)
        if opcode not in self.opcodes:
            logger.warning(f"Unhandled opcode at ${self.pc:04x}")
        self.pc += 1
        handler = self.opcodes.get(opcode, self.brk)
        handler()

        if self.status & (1 << self.STATUS_I) > 0 and self.status & (1 << self.STATUS_B) > 0:
            self.status &= ~(1 << self.STATUS_B)
            return StepResult.BRK
        return StepResult.NORMAL

    def update_zero_flag(self, result: int) -> None:
        """Update the zero (Z) flag of the status register based on the result of an operation.

        Args:
            result: Byte resulting from an operation that updates the status register.

        """
        self.status &= ~(1 << self.STATUS_Z)
        self.status |= (result == 0) << self.STATUS_Z

    def update_negative_flag(self, result: int) -> None:
        """Update the negative (N) flag of the status register based on the result of an operation.

        Args:
            result: Byte resulting from an operation that updates the status register.

        """
        result_msb = (result >> 7) & 0x01
        self.status &= ~(1 << self.STATUS_N)
        self.status |= result_msb << self.STATUS_N

    def resolve_address(self, mode: AddressingMode) -> tuple[int, bool]:  # noqa: PLR0915
        """Resolve the effective address for a given addressing mode.

        Args:
            mode: The addressing mode to resolve.

        Returns:
            (addr, page_boundary_crossed): The effective memory address and if a page boundary
            has been crossed by indexing.

        """
        addr: int
        page_boundary_crossed = False
        match mode:
            case AddressingMode.IMMEDIATE:
                addr = self.pc
                self.pc += 1
            case AddressingMode.ZERO_PAGE:
                addr = self.memory.read(self.pc)
                self.pc += 1
            case AddressingMode.ZERO_PAGE_X:
                zero_page_location = self.memory.read(self.pc)
                addr = (zero_page_location + self.x) & 0xff
                self.pc += 1
            case AddressingMode.ZERO_PAGE_Y:
                zero_page_location = self.memory.read(self.pc)
                addr = (zero_page_location + self.y) & 0xff
                self.pc += 1
            case AddressingMode.ABSOLUTE:
                addr_base_lo = self.memory.read(self.pc)
                addr_base_hi = self.memory.read(self.pc + 1)
                addr = (addr_base_hi << 8) | addr_base_lo
                self.pc += 2
            case AddressingMode.ABSOLUTE_X:
                addr_base_lo = self.memory.read(self.pc)
                addr_base_hi = self.memory.read(self.pc + 1)
                addr_base = (addr_base_hi << 8) | addr_base_lo
                addr = (addr_base + self.x) & 0xffff
                page_boundary_crossed = (addr_base & 0xff00) != (addr & 0xff00)
                self.pc += 2
            case AddressingMode.ABSOLUTE_Y:
                addr_base_lo = self.memory.read(self.pc)
                addr_base_hi = self.memory.read(self.pc + 1)
                addr_base = (addr_base_hi << 8) | addr_base_lo
                addr = (addr_base + self.y) & 0xffff
                page_boundary_crossed = (addr_base & 0xff00) != (addr & 0xff00)
                self.pc += 2
            case AddressingMode.INDIRECT_X:
                addr_zp = (self.memory.read(self.pc) + self.x) & 0xff
                addr_indirect_lo = self.memory.read(addr_zp)
                addr_indirect_hi = self.memory.read((addr_zp + 1) & 0xff)
                addr = (addr_indirect_hi << 8) | addr_indirect_lo
                self.pc += 1
            case AddressingMode.INDIRECT_Y:
                addr_zp = self.memory.read(self.pc)
                addr_base_lo = self.memory.read(addr_zp)
                addr_base_hi = self.memory.read((addr_zp + 1) & 0xff)
                addr_base = (addr_base_hi << 8) | addr_base_lo
                addr = (addr_base + self.y) & 0xffff
                page_boundary_crossed = (addr_base & 0xff00) != (addr & 0xff00)
                self.pc += 1
            case _:
                assert_never(mode)

        return addr, page_boundary_crossed

    def push_byte_to_stack(self, byte: int) -> None:
        """Push a byte to the stack and update stack pointer.

        Note: This method does not update the status register or perform underflow checks.

        Args:
            byte: Byte to push onto the stack.

        """
        self.memory.write(self.STACK_ROOT + self.sp, byte)
        self.sp = (self.sp - 1) & 0xff

    def pull_byte_from_stack(self) -> int:
        """Pull a byte from the stack and update the stack pointer.

        Note: This method does not update the status register or perform overflow checks.

        Returns:
            byte: Byte to push onto the stack.

        """
        self.sp = (self.sp + 1) & 0xff
        return self.memory.read(self.STACK_ROOT + self.sp)

    def brk(self) -> None:
        """Execute BRK instruction."""
        self.status |= (1 << self.STATUS_I) | (1 << self.STATUS_B)
        self.pc += 1
        self.cycles += 7
        pc_lo = self.pc & 0xff
        pc_hi = (self.pc >> 8) & 0xff
        self.push_byte_to_stack(pc_hi)
        self.push_byte_to_stack(pc_lo)
        self.push_byte_to_stack(self.status)

    # Flag instructions

    def clc(self) -> None:
        """Execute the CLear Carry (CLC) instruction."""
        self.status &= ~(1 << self.STATUS_C)
        self.cycles += 2

    def sec(self) -> None:
        """Execute the SEt Carry (SEC) instruction."""
        self.status |= (1 << self.STATUS_C)
        self.cycles += 2

    def cli(self) -> None:
        """Execute the CLear Interrupt (CLI) instruction."""
        self.status &= ~(1 << self.STATUS_I)
        self.cycles += 2

    def sei(self) -> None:
        """Execute the SEt Interrupt (SEI) instruction."""
        self.status |= (1 << self.STATUS_I)
        self.cycles += 2

    def cld(self) -> None:
        """Execute the CLear Decimal (CLD) instruction."""
        self.status &= ~(1 << self.STATUS_D)
        self.cycles += 2

    def sed(self) -> None:
        """Execute the SEt Decimal (SED) instruction."""
        self.status |= (1 << self.STATUS_D)
        self.cycles += 2

    def clv(self) -> None:
        """Execute the CLear oVerflow (CLV) instruction."""
        self.status &= ~(1 << self.STATUS_V)
        self.cycles += 2

    # Register loading

    def lda(self, mode: AddressingMode) -> None:
        """Execute LDA instruction with specified addressing mode."""
        # load value into register
        addr, page_boundary_crossed = self.resolve_address(mode)
        self.a = self.memory.read(addr)

        # update cycle counter
        cycle_counts = {
            AddressingMode.IMMEDIATE: 2,
            AddressingMode.ZERO_PAGE: 3,
            AddressingMode.ZERO_PAGE_X: 4,
            AddressingMode.ABSOLUTE: 4,
            AddressingMode.ABSOLUTE_X: 4,
            AddressingMode.ABSOLUTE_Y: 4,
            AddressingMode.INDIRECT_X: 6,
            AddressingMode.INDIRECT_Y: 5,
        }
        extra_cycle_page_boundary = [AddressingMode.ABSOLUTE_X, AddressingMode.ABSOLUTE_Y, AddressingMode.INDIRECT_Y]
        self.cycles += cycle_counts[mode]
        if page_boundary_crossed and mode in extra_cycle_page_boundary:
            self.cycles += 1

        self.update_zero_flag(self.a)
        self.update_negative_flag(self.a)

    def ldx(self, mode: AddressingMode) -> None:
        """Execute LDX instruction with specified addressing mode."""
        # load value into register
        addr, page_boundary_crossed = self.resolve_address(mode)
        self.x = self.memory.read(addr)

        # update cycle counter
        cycle_counts = {
            AddressingMode.IMMEDIATE: 2,
            AddressingMode.ZERO_PAGE: 3,
            AddressingMode.ZERO_PAGE_Y: 4,
            AddressingMode.ABSOLUTE: 4,
            AddressingMode.ABSOLUTE_Y: 4,
        }
        extra_cycle_page_boundary = [AddressingMode.ABSOLUTE_Y]
        self.cycles += cycle_counts[mode]
        if page_boundary_crossed and mode in extra_cycle_page_boundary:
            self.cycles += 1

        self.update_zero_flag(self.x)
        self.update_negative_flag(self.x)

    def ldy(self, mode: AddressingMode) -> None:
        """Execute LDY instruction with specified addressing mode."""
        # load value into register
        addr, page_boundary_crossed = self.resolve_address(mode)
        self.y = self.memory.read(addr)

        # update cycle counter
        cycle_counts = {
            AddressingMode.IMMEDIATE: 2,
            AddressingMode.ZERO_PAGE: 3,
            AddressingMode.ZERO_PAGE_X: 4,
            AddressingMode.ABSOLUTE: 4,
            AddressingMode.ABSOLUTE_X: 4,
        }
        extra_cycle_page_boundary = [AddressingMode.ABSOLUTE_X]
        self.cycles += cycle_counts[mode]
        if page_boundary_crossed and mode in extra_cycle_page_boundary:
            self.cycles += 1

        self.update_zero_flag(self.y)
        self.update_negative_flag(self.y)

    # Register storing

    def sta(self, mode: AddressingMode) -> None:
        """Execute the STore A (STA) instruction."""
        # write register value to memory
        addr, _ = self.resolve_address(mode)
        self.memory.write(addr, self.a)

        # update cycle counter
        cycle_counts = {
            AddressingMode.ZERO_PAGE: 3,
            AddressingMode.ZERO_PAGE_X: 4,
            AddressingMode.ABSOLUTE: 4,
            AddressingMode.ABSOLUTE_X: 5,
            AddressingMode.ABSOLUTE_Y: 5,
            AddressingMode.INDIRECT_X: 6,
            AddressingMode.INDIRECT_Y: 6,
        }
        self.cycles += cycle_counts[mode]

    def stx(self, mode: AddressingMode) -> None:
        """Execute the STore X (STX) instruction."""
        # write register value to memory
        addr, _ = self.resolve_address(mode)
        self.memory.write(addr, self.x)

        # update cycle counter
        cycle_counts = {
            AddressingMode.ZERO_PAGE: 3,
            AddressingMode.ZERO_PAGE_Y: 4,
            AddressingMode.ABSOLUTE: 4,
        }
        self.cycles += cycle_counts[mode]

    def sty(self, mode: AddressingMode) -> None:
        """Execute the STore Y (STY) instruction."""
        # write register value to memory
        addr, _ = self.resolve_address(mode)
        self.memory.write(addr, self.y)

        # update cycle counter
        cycle_counts = {
            AddressingMode.ZERO_PAGE: 3,
            AddressingMode.ZERO_PAGE_X: 4,
            AddressingMode.ABSOLUTE: 4,
        }
        self.cycles += cycle_counts[mode]
