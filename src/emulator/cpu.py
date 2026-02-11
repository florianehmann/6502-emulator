"""CPU Logic."""

import enum
import logging
from collections.abc import Callable
from functools import partial
from typing import ClassVar, Literal

from emulator.memory import Memory
from emulator.utils import assert_never, dec_to_bcd

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

    LOAD_CYCLE_COUNTS: ClassVar[dict[AddressingMode, int]] = {
        AddressingMode.IMMEDIATE: 2,
        AddressingMode.ZERO_PAGE: 3,
        AddressingMode.ZERO_PAGE_X: 4,
        AddressingMode.ZERO_PAGE_Y: 4,
        AddressingMode.ABSOLUTE: 4,
        AddressingMode.ABSOLUTE_X: 4,
        AddressingMode.ABSOLUTE_Y: 4,
        AddressingMode.INDIRECT_X: 6,
        AddressingMode.INDIRECT_Y: 5,
    }

    LOAD_EXTRA_CYCLE_MODES: ClassVar[tuple[AddressingMode, ...]] = (
        AddressingMode.ABSOLUTE_X,
        AddressingMode.ABSOLUTE_Y,
        AddressingMode.INDIRECT_Y,
    )

    STORE_CYCLE_COUNTS: ClassVar[dict[AddressingMode, int]] = {
        AddressingMode.ZERO_PAGE: 3,
        AddressingMode.ZERO_PAGE_X: 4,
        AddressingMode.ZERO_PAGE_Y: 4,
        AddressingMode.ABSOLUTE: 4,
        AddressingMode.ABSOLUTE_X: 5,
        AddressingMode.ABSOLUTE_Y: 5,
        AddressingMode.INDIRECT_X: 6,
        AddressingMode.INDIRECT_Y: 6,
    }

    UNARY_CYCLE_COUNTS: ClassVar[dict[AddressingMode, int]] = {
        AddressingMode.ZERO_PAGE: 5,
        AddressingMode.ZERO_PAGE_X: 6,
        AddressingMode.ABSOLUTE: 6,
        AddressingMode.ABSOLUTE_X: 7,
    }

    BINARY_CYCLE_COUNTS: ClassVar[dict[AddressingMode, int]] = {
        AddressingMode.IMMEDIATE: 2,
        AddressingMode.ZERO_PAGE: 3,
        AddressingMode.ZERO_PAGE_X: 4,
        AddressingMode.ZERO_PAGE_Y: 4,
        AddressingMode.ABSOLUTE: 4,
        AddressingMode.ABSOLUTE_X: 4,
        AddressingMode.ABSOLUTE_Y: 4,
        AddressingMode.INDIRECT_X: 6,
        AddressingMode.INDIRECT_Y: 5,
    }

    BINARY_EXTRA_CYCLE_MODES: ClassVar[tuple[AddressingMode, ...]] = (
        AddressingMode.ABSOLUTE_X,
        AddressingMode.ABSOLUTE_Y,
        # INDIRECT_Y only on some
    )

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
            0x01: partial(self.ora, mode=AddressingMode.INDIRECT_X),
            0x05: partial(self.ora, mode=AddressingMode.ZERO_PAGE),
            0x06: partial(self.asl, mode=AddressingMode.ZERO_PAGE),
            0x09: partial(self.ora, mode=AddressingMode.IMMEDIATE),
            0x0a: partial(self.asl, mode=None),
            0x0d: partial(self.ora, mode=AddressingMode.ABSOLUTE),
            0x0e: partial(self.asl, mode=AddressingMode.ABSOLUTE),
            0x10: partial(self.branch, flag_index=self.STATUS_N, flag_value=0),
            0x11: partial(self.ora, mode=AddressingMode.INDIRECT_Y),
            0x15: partial(self.ora, mode=AddressingMode.ZERO_PAGE_X),
            0x16: partial(self.asl, mode=AddressingMode.ZERO_PAGE_X),
            0x18: self.clc,
            0x19: partial(self.ora, mode=AddressingMode.ABSOLUTE_Y),
            0x1d: partial(self.ora, mode=AddressingMode.ABSOLUTE_X),
            0x1e: partial(self.asl, mode=AddressingMode.ABSOLUTE_X),
            0x21: partial(self.and_op, mode=AddressingMode.INDIRECT_X),
            0x25: partial(self.and_op, mode=AddressingMode.ZERO_PAGE),
            0x26: partial(self.rol, mode=AddressingMode.ZERO_PAGE),
            0x29: partial(self.and_op, mode=AddressingMode.IMMEDIATE),
            0x2a: partial(self.rol, mode=None),
            0x2d: partial(self.and_op, mode=AddressingMode.ABSOLUTE),
            0x2e: partial(self.rol, mode=AddressingMode.ABSOLUTE),
            0x30: partial(self.branch, flag_index=self.STATUS_N, flag_value=1),
            0x31: partial(self.and_op, mode=AddressingMode.INDIRECT_Y),
            0x35: partial(self.and_op, mode=AddressingMode.ZERO_PAGE_X),
            0x36: partial(self.rol, mode=AddressingMode.ZERO_PAGE_X),
            0x38: self.sec,
            0x39: partial(self.and_op, mode=AddressingMode.ABSOLUTE_Y),
            0x3d: partial(self.and_op, mode=AddressingMode.ABSOLUTE_X),
            0x3e: partial(self.rol, mode=AddressingMode.ABSOLUTE_X),
            0x41: partial(self.eor, mode=AddressingMode.INDIRECT_X),
            0x45: partial(self.eor, mode=AddressingMode.ZERO_PAGE),
            0x46: partial(self.lsr, mode=AddressingMode.ZERO_PAGE),
            0x49: partial(self.eor, mode=AddressingMode.IMMEDIATE),
            0x4a: partial(self.lsr, mode=None),
            0x4c: partial(self.jmp, mode="absolute"),
            0x4d: partial(self.eor, mode=AddressingMode.ABSOLUTE),
            0x4e: partial(self.lsr, mode=AddressingMode.ABSOLUTE),
            0x50: partial(self.branch, flag_index=self.STATUS_V, flag_value=0),
            0x51: partial(self.eor, mode=AddressingMode.INDIRECT_Y),
            0x55: partial(self.eor, mode=AddressingMode.ZERO_PAGE_X),
            0x56: partial(self.lsr, mode=AddressingMode.ZERO_PAGE_X),
            0x58: self.cli,
            0x59: partial(self.eor, mode=AddressingMode.ABSOLUTE_Y),
            0x5d: partial(self.eor, mode=AddressingMode.ABSOLUTE_X),
            0x5e: partial(self.lsr, mode=AddressingMode.ABSOLUTE_X),
            0x61: partial(self.adc, mode=AddressingMode.INDIRECT_X),
            0x65: partial(self.adc, mode=AddressingMode.ZERO_PAGE),
            0x66: partial(self.ror, mode=AddressingMode.ZERO_PAGE),
            0x69: partial(self.adc, mode=AddressingMode.IMMEDIATE),
            0x6a: partial(self.ror, mode=None),
            0x6c: partial(self.jmp, mode="indirect"),
            0x6d: partial(self.adc, mode=AddressingMode.ABSOLUTE),
            0x6e: partial(self.ror, mode=AddressingMode.ABSOLUTE),
            0x70: partial(self.branch, flag_index=self.STATUS_V, flag_value=1),
            0x71: partial(self.adc, mode=AddressingMode.INDIRECT_Y),
            0x75: partial(self.adc, mode=AddressingMode.ZERO_PAGE_X),
            0x76: partial(self.ror, mode=AddressingMode.ZERO_PAGE_X),
            0x78: self.sei,
            0x79: partial(self.adc, mode=AddressingMode.ABSOLUTE_Y),
            0x7d: partial(self.adc, mode=AddressingMode.ABSOLUTE_X),
            0x7e: partial(self.ror, mode=AddressingMode.ABSOLUTE_X),
            0x81: partial(self.sta, mode=AddressingMode.INDIRECT_X),
            0x84: partial(self.sty, mode=AddressingMode.ZERO_PAGE),
            0x85: partial(self.sta, mode=AddressingMode.ZERO_PAGE),
            0x86: partial(self.stx, mode=AddressingMode.ZERO_PAGE),
            0x88: self.dey,
            0x8a: self.txa,
            0x8c: partial(self.sty, mode=AddressingMode.ABSOLUTE),
            0x8d: partial(self.sta, mode=AddressingMode.ABSOLUTE),
            0x8e: partial(self.stx, mode=AddressingMode.ABSOLUTE),
            0x90: partial(self.branch, flag_index=self.STATUS_C, flag_value=0),
            0x91: partial(self.sta, mode=AddressingMode.INDIRECT_Y),
            0x94: partial(self.sty, mode=AddressingMode.ZERO_PAGE_X),
            0x95: partial(self.sta, mode=AddressingMode.ZERO_PAGE_X),
            0x96: partial(self.stx, mode=AddressingMode.ZERO_PAGE_Y),
            0x98: self.tya,
            0x99: partial(self.sta, mode=AddressingMode.ABSOLUTE_Y),
            0x9a: self.txs,
            0x9d: partial(self.sta, mode=AddressingMode.ABSOLUTE_X),
            0xa0: partial(self.ldy, mode=AddressingMode.IMMEDIATE),
            0xa1: partial(self.lda, mode=AddressingMode.INDIRECT_X),
            0xa2: partial(self.ldx, mode=AddressingMode.IMMEDIATE),
            0xa4: partial(self.ldy, mode=AddressingMode.ZERO_PAGE),
            0xa5: partial(self.lda, mode=AddressingMode.ZERO_PAGE),
            0xa6: partial(self.ldx, mode=AddressingMode.ZERO_PAGE),
            0xa8: self.tay,
            0xa9: partial(self.lda, mode=AddressingMode.IMMEDIATE),
            0xaa: self.tax,
            0xac: partial(self.ldy, mode=AddressingMode.ABSOLUTE),
            0xad: partial(self.lda, mode=AddressingMode.ABSOLUTE),
            0xae: partial(self.ldx, mode=AddressingMode.ABSOLUTE),
            0xb0: partial(self.branch, flag_index=self.STATUS_C, flag_value=1),
            0xb1: partial(self.lda, mode=AddressingMode.INDIRECT_Y),
            0xb4: partial(self.ldy, mode=AddressingMode.ZERO_PAGE_X),
            0xb5: partial(self.lda, mode=AddressingMode.ZERO_PAGE_X),
            0xb6: partial(self.ldx, mode=AddressingMode.ZERO_PAGE_Y),
            0xb8: self.clv,
            0xb9: partial(self.lda, mode=AddressingMode.ABSOLUTE_Y),
            0xba: self.tsx,
            0xbc: partial(self.ldy, mode=AddressingMode.ABSOLUTE_X),
            0xbd: partial(self.lda, mode=AddressingMode.ABSOLUTE_X),
            0xbe: partial(self.ldx, mode=AddressingMode.ABSOLUTE_Y),
            0xc6: partial(self.dec, mode=AddressingMode.ZERO_PAGE),
            0xc8: self.iny,
            0xca: self.dex,
            0xce: partial(self.dec, mode=AddressingMode.ABSOLUTE),
            0xd0: partial(self.branch, flag_index=self.STATUS_Z, flag_value=0),
            0xd6: partial(self.dec, mode=AddressingMode.ZERO_PAGE_X),
            0xde: partial(self.dec, mode=AddressingMode.ABSOLUTE),
            0xd8: self.cld,
            0xe1: partial(self.sbc, mode=AddressingMode.INDIRECT_X),
            0xe5: partial(self.sbc, mode=AddressingMode.ZERO_PAGE),
            0xe6: partial(self.inc, mode=AddressingMode.ZERO_PAGE),
            0xe8: self.inx,
            0xe9: partial(self.sbc, mode=AddressingMode.IMMEDIATE),
            0xea: self.nop,
            0xed: partial(self.sbc, mode=AddressingMode.ABSOLUTE),
            0xee: partial(self.inc, mode=AddressingMode.ABSOLUTE),
            0xf0: partial(self.branch, flag_index=self.STATUS_Z, flag_value=1),
            0xf1: partial(self.sbc, mode=AddressingMode.INDIRECT_Y),
            0xf5: partial(self.sbc, mode=AddressingMode.ZERO_PAGE_X),
            0xf6: partial(self.inc, mode=AddressingMode.ZERO_PAGE_X),
            0xf8: self.sed,
            0xf9: partial(self.sbc, mode=AddressingMode.ABSOLUTE_Y),
            0xfd: partial(self.sbc, mode=AddressingMode.ABSOLUTE_X),
            0xfe: partial(self.inc, mode=AddressingMode.ABSOLUTE_X),
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

    def update_overflow_flag(self, a_initial: int, operand: int, result: int) -> None:
        """Update the overflow (V) flag of the status register based on the result of an operation.

        Args:
            a_initial: Accumulator value before operation.
            operand: Operand of potentially overflowing operation.
            result: Accumulator value after operation.

        """
        inputs_same_sign = ~(a_initial ^ operand) & 0x80
        result_sign_different_from_inputs = (a_initial ^ result) & 0x80
        v = inputs_same_sign & result_sign_different_from_inputs
        v = (v >> 7) & 1

        self.status &= ~(1 << self.STATUS_V)
        self.status |= v << self.STATUS_V

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
            byte: Byte pulled from the stack.

        """
        self.sp = (self.sp + 1) & 0xff
        return self.memory.read(self.STACK_ROOT + self.sp)

    def branch(self, flag_index: int, flag_value: int) -> None:
        """Branch to relative address if specified flag is set or clear.

        Args:
            flag_index: Index of the flag in the status register to check.
            flag_value: The value the flag should have for the branch to be taken (0 or 1).

        """
        int8_min = 0x80
        should_branch = ((self.status >> flag_index) & 1) == flag_value
        if should_branch:
            offset = self.memory.read(self.pc)
            self.pc += 1

            # convert negative offsets to signed values
            if offset >= int8_min:
                offset -= 0x100

            # jump
            old_pc = self.pc
            self.pc = (self.pc + offset) & 0xffff
            self.cycles += 3

            # add another cycle if page boundary is crossed
            if (old_pc & 0xff00) != (self.pc & 0xff00):
                self.cycles += 1
        else:
            self.pc += 1
            self.cycles += 2

    # System instructions

    def brk(self) -> None:
        """Execute the BReaK (BRK) instruction."""
        self.status |= (1 << self.STATUS_I) | (1 << self.STATUS_B)
        self.pc += 1
        self.cycles += 7
        pc_lo = self.pc & 0xff
        pc_hi = (self.pc >> 8) & 0xff
        self.push_byte_to_stack(pc_hi)
        self.push_byte_to_stack(pc_lo)
        self.push_byte_to_stack(self.status)

    def jmp(self, mode: Literal["absolute", "indirect"]) -> None:
        """Execute the JuMP (JMP) instruction.

        Note: This implementation correctly reproduces the hardware bug of the original NMOS 6502 in which the high byte
        of the target address is fetched from the beginning of the same page when the low byte is 0xff.
        """
        addr_lo = self.memory.read(self.pc)
        addr_hi = self.memory.read((self.pc + 1) & 0xffff)
        addr = (addr_hi << 8) | addr_lo
        if mode == "absolute":
            self.pc = addr
        elif mode == "indirect":
            addr_lo = self.memory.read(addr)
            # this reproduces the NMOS 6502's hardware bug
            addr_incremented = (addr & 0xff00) | ((addr + 1) & 0x00ff)
            addr_hi = self.memory.read(addr_incremented)
            self.pc = (addr_hi << 8) | addr_lo
        self.cycles += 3 if mode == "absolute" else 5

    def nop(self) -> None:
        """Execute No OPeration (NOP) instruction."""
        self.cycles += 2

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
        self.cycles += self.LOAD_CYCLE_COUNTS[mode]
        if page_boundary_crossed and mode in self.LOAD_EXTRA_CYCLE_MODES:
            self.cycles += 1

        self.update_zero_flag(self.a)
        self.update_negative_flag(self.a)

    def ldx(self, mode: AddressingMode) -> None:
        """Execute LDX instruction with specified addressing mode."""
        # load value into register
        addr, page_boundary_crossed = self.resolve_address(mode)
        self.x = self.memory.read(addr)

        # update cycle counter
        self.cycles += self.LOAD_CYCLE_COUNTS[mode]
        if page_boundary_crossed and mode in self.LOAD_EXTRA_CYCLE_MODES:
            self.cycles += 1

        self.update_zero_flag(self.x)
        self.update_negative_flag(self.x)

    def ldy(self, mode: AddressingMode) -> None:
        """Execute LDY instruction with specified addressing mode."""
        # load value into register
        addr, page_boundary_crossed = self.resolve_address(mode)
        self.y = self.memory.read(addr)

        # update cycle counter
        self.cycles += self.LOAD_CYCLE_COUNTS[mode]
        if page_boundary_crossed and mode in self.LOAD_EXTRA_CYCLE_MODES:
            self.cycles += 1

        self.update_zero_flag(self.y)
        self.update_negative_flag(self.y)

    # Register storing

    def sta(self, mode: AddressingMode) -> None:
        """Execute the STore A (STA) instruction."""
        # write register value to memory
        addr, _ = self.resolve_address(mode)
        self.memory.write(addr, self.a)
        self.cycles += self.STORE_CYCLE_COUNTS[mode]

    def stx(self, mode: AddressingMode) -> None:
        """Execute the STore X (STX) instruction."""
        # write register value to memory
        addr, _ = self.resolve_address(mode)
        self.memory.write(addr, self.x)
        self.cycles += self.STORE_CYCLE_COUNTS[mode]

    def sty(self, mode: AddressingMode) -> None:
        """Execute the STore Y (STY) instruction."""
        # write register value to memory
        addr, _ = self.resolve_address(mode)
        self.memory.write(addr, self.y)
        self.cycles += self.STORE_CYCLE_COUNTS[mode]

    # Register transfer

    def tax(self) -> None:
        """Execute the Transfer Accumulator to X (TAX) instruction."""
        self.x = self.a
        self.cycles += 2
        self.update_zero_flag(self.x)
        self.update_negative_flag(self.x)

    def tay(self) -> None:
        """Execute the Transfer Accumulator to Y (TAY) instruction."""
        self.y = self.a
        self.cycles += 2
        self.update_zero_flag(self.y)
        self.update_negative_flag(self.y)

    def tsx(self) -> None:
        """Execute the Transfer Stack Pointer to X (TSX) instruction."""
        self.x = self.sp
        self.cycles += 2
        self.update_zero_flag(self.x)
        self.update_negative_flag(self.x)

    def txa(self) -> None:
        """Execute the Transfer X to Accumulator (TXA) instruction."""
        self.a = self.x
        self.cycles += 2
        self.update_zero_flag(self.a)
        self.update_negative_flag(self.a)

    def txs(self) -> None:
        """Execute the Transfer X to Stack Pointer (TXS) instruction."""
        self.sp = self.x
        self.cycles += 2

    def tya(self) -> None:
        """Execute the Transfer Y to Accumulator (TYA) instruction."""
        self.a = self.y
        self.cycles += 2
        self.update_zero_flag(self.a)
        self.update_negative_flag(self.a)

    # Unary arithmetic

    def dec(self, mode: AddressingMode) -> None:
        """Execute the DECrement (DEC) instruction."""
        addr, _ = self.resolve_address(mode)
        byte = self.memory.read(addr)
        byte = (byte - 1) & 0xff
        self.memory.write(addr, byte)

        self.cycles += self.UNARY_CYCLE_COUNTS[mode]

        self.update_zero_flag(byte)
        self.update_negative_flag(byte)

    def dex(self) -> None:
        """Execute the DEcrement X (DEX) instruction."""
        self.x = (self.x - 1) & 0xff

        self.cycles += 2

        self.update_zero_flag(self.x)
        self.update_negative_flag(self.x)

    def dey(self) -> None:
        """Execute the DEcrement Y (DEY) instruction."""
        self.y = (self.y - 1) & 0xff

        self.cycles += 2

        self.update_zero_flag(self.y)
        self.update_negative_flag(self.y)

    def inc(self, mode: AddressingMode) -> None:
        """Execute the INCrement (INC) instruction."""
        addr, _ = self.resolve_address(mode)
        byte = self.memory.read(addr)
        byte = (byte + 1) & 0xff
        self.memory.write(addr, byte)

        self.cycles += self.UNARY_CYCLE_COUNTS[mode]

        self.update_zero_flag(byte)
        self.update_negative_flag(byte)

    def inx(self) -> None:
        """Execute the INcrement X (INX) instruction."""
        self.x = (self.x + 1) & 0xff

        self.cycles += 2

        self.update_zero_flag(self.x)
        self.update_negative_flag(self.x)

    def iny(self) -> None:
        """Execute the INcrement Y (INY) instruction."""
        self.y = (self.y + 1) & 0xff

        self.cycles += 2

        self.update_zero_flag(self.y)
        self.update_negative_flag(self.y)

    def asl(self, mode: AddressingMode | None) -> None:
        """Execute the Arithmetic Shift Left (ASL) instruction.

        If `mode` is None, ASL is performed on the accumulator.
        """
        value: int
        carry: int
        if mode:
            addr, _ = self.resolve_address(mode)
            value = self.memory.read(addr)

            carry = (value >> 7) & 1
            value = (value << 1) & 0xff

            self.memory.write(addr, value)
        else:
            value = self.a

            carry = (value >> 7) & 1
            value = (value << 1) & 0xff

            self.a = value

        self.status &= ~(1 << self.STATUS_C)
        self.status |= (carry << self.STATUS_C)

        self.cycles += self.UNARY_CYCLE_COUNTS[mode] if mode else 2

        self.update_zero_flag(value)
        self.update_negative_flag(value)

    def lsr(self, mode: AddressingMode | None) -> None:
        """Execute the Logic Shift Right (LSR) instruction.

        If `mode` is None, LSR is performed on the accumulator.
        """
        value: int
        carry: int
        if mode:
            addr, _ = self.resolve_address(mode)
            value = self.memory.read(addr)

            carry = value & 1
            value >>= 1

            self.memory.write(addr, value)
        else:
            value = self.a

            carry = value & 1
            value >>= 1

            self.a = value

        self.status &= ~(1 << self.STATUS_C)
        self.status |= (carry << self.STATUS_C)

        self.cycles += self.UNARY_CYCLE_COUNTS[mode] if mode else 2

        self.update_zero_flag(value)
        self.update_negative_flag(value)  # Always zero here

    def rol(self, mode: AddressingMode | None) -> None:
        """Execute the Rotate Left (ROL) instruction.

        If `mode` is None, ROL is performed on the accumulator.
        """
        buffer = (self.status >> self.STATUS_C) & 1
        value: int
        carry: int
        if mode:
            addr, _ = self.resolve_address(mode)
            value = self.memory.read(addr)

            carry = (value >> 7) & 1
            value = (value << 1 | buffer) & 0xff

            self.memory.write(addr, value)
        else:
            value = self.a

            carry = (value >> 7) & 1
            value = (value << 1 | buffer) & 0xff

            self.a = value

        self.status &= ~(1 << self.STATUS_C)
        self.status |= (carry << self.STATUS_C)

        self.cycles += self.UNARY_CYCLE_COUNTS[mode] if mode else 2

        self.update_zero_flag(value)
        self.update_negative_flag(value)

    def ror(self, mode: AddressingMode | None) -> None:
        """Execute the Rotate Right (ROR) instruction.

        If `mode` is None, ROR is performed on the accumulator.
        """
        buffer = (self.status >> self.STATUS_C) & 1
        value: int
        carry: int
        if mode:
            addr, _ = self.resolve_address(mode)
            value = self.memory.read(addr)

            carry = value & 1
            value = ((buffer << 8) | value) >> 1

            self.memory.write(addr, value)
        else:
            value = self.a

            carry = value & 1
            value = ((buffer << 8) | value) >> 1

            self.a = value

        self.status &= ~(1 << self.STATUS_C)
        self.status |= (carry << self.STATUS_C)

        self.cycles += self.UNARY_CYCLE_COUNTS[mode] if mode else 2

        self.update_zero_flag(value)
        self.update_negative_flag(value)

    # Binary arithmetic (ADC, AND, EOR, ORA, SBC)

    def adc(self, mode: AddressingMode) -> None:
        """Execute the ADd with Carry (ADC) instruction."""
        addr, page_boundary_crossed = self.resolve_address(mode)
        operand = self.memory.read(addr)

        a_initial = self.a
        carry_in = (self.status >> self.STATUS_C) & 1
        binary_intermediate_sum = self.a + operand + carry_in
        carry_out = binary_intermediate_sum >> 8
        binary_result = binary_intermediate_sum & 0xff

        if (self.status & (1 << self.STATUS_D)) == 0:
            self.a = binary_result
        else:
            lo_nibble_a = a_initial & 0xF
            hi_nibble_a = a_initial >> 4
            lo_nibble_operand = operand & 0xF
            hi_nibble_operand = operand >> 4

            a_dec = lo_nibble_a + hi_nibble_a * 10
            operand_dec = lo_nibble_operand + hi_nibble_operand * 10
            intermediate_sum = a_dec + operand_dec + carry_in

            carry_out = 1 if intermediate_sum >= 100 else 0  # noqa: PLR2004
            intermediate_sum = intermediate_sum - 100 if carry_out else intermediate_sum
            self.a = dec_to_bcd(intermediate_sum)

        self.status &= ~(1 << self.STATUS_C)
        self.status |= (carry_out << self.STATUS_C)
        self.update_zero_flag(binary_result)
        self.update_negative_flag(binary_result)
        self.update_overflow_flag(a_initial, operand, binary_result)

        self.cycles += self.BINARY_CYCLE_COUNTS[mode]
        if page_boundary_crossed and mode in (*self.BINARY_EXTRA_CYCLE_MODES, AddressingMode.INDIRECT_Y):
            self.cycles += 1

    def and_op(self, mode: AddressingMode) -> None:
        """Execute the AND instruction."""
        addr, page_boundary_crossed = self.resolve_address(mode)
        operand = self.memory.read(addr)

        self.a &= operand

        self.update_zero_flag(self.a)
        self.update_negative_flag(self.a)

        self.cycles += self.BINARY_CYCLE_COUNTS[mode]
        if page_boundary_crossed and mode in (*self.BINARY_EXTRA_CYCLE_MODES, AddressingMode.INDIRECT_Y):
            self.cycles += 1

    def eor(self, mode: AddressingMode) -> None:
        """Execute the Exclusive OR instruction."""
        addr, page_boundary_crossed = self.resolve_address(mode)
        operand = self.memory.read(addr)

        self.a ^= operand

        self.update_zero_flag(self.a)
        self.update_negative_flag(self.a)

        self.cycles += self.BINARY_CYCLE_COUNTS[mode]
        if page_boundary_crossed and mode in self.BINARY_EXTRA_CYCLE_MODES:
            self.cycles += 1

    def ora(self, mode: AddressingMode) -> None:
        """Execute the OR with Accumulator instruction."""
        addr, page_boundary_crossed = self.resolve_address(mode)
        operand = self.memory.read(addr)

        self.a |= operand

        self.update_zero_flag(self.a)
        self.update_negative_flag(self.a)

        self.cycles += self.BINARY_CYCLE_COUNTS[mode]
        if page_boundary_crossed and mode in self.BINARY_EXTRA_CYCLE_MODES:
            self.cycles += 1

    def sbc(self, mode: AddressingMode) -> None:
        """Execute the SuBtract with Carry / borrow (SBC) instruction."""
        addr, page_boundary_crossed = self.resolve_address(mode)
        operand = self.memory.read(addr)

        a_initial = self.a
        carry_in = (self.status >> self.STATUS_C) & 1
        binary_intermediate_difference = self.a + (~operand & 0xff) + carry_in
        carry_out = binary_intermediate_difference >> 8
        binary_result = binary_intermediate_difference & 0xff

        if (self.status & (1 << self.STATUS_D)) == 0:
            self.a = binary_result
        else:
            lo_nibble_a = a_initial & 0xF
            hi_nibble_a = a_initial >> 4
            lo_nibble_operand = operand & 0xF
            hi_nibble_operand = operand >> 4

            a_dec = lo_nibble_a + hi_nibble_a * 10
            operand_dec = lo_nibble_operand + hi_nibble_operand * 10
            intermediate_sum = a_dec - operand_dec + carry_in - 1

            carry_out = 1 if intermediate_sum >= 0 else 0
            intermediate_sum = intermediate_sum if carry_out else intermediate_sum + 100
            self.a = dec_to_bcd(intermediate_sum)

        self.status &= ~(1 << self.STATUS_C)
        self.status |= (carry_out << self.STATUS_C)
        self.update_zero_flag(binary_result)
        self.update_negative_flag(binary_result)
        self.update_overflow_flag(a_initial, ~operand & 0xff, binary_result)

        self.cycles += self.BINARY_CYCLE_COUNTS[mode]
        if page_boundary_crossed and mode in (*self.BINARY_EXTRA_CYCLE_MODES, AddressingMode.INDIRECT_Y):
            self.cycles += 1

    # Binary logic (BIT, CMP, CPX, CPY)
