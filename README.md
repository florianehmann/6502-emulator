# another6502

> Did you ever think there just aren't enough Python-based 6502 emulators out there?
> Well, too bad, 'cause here is yet `another6502`!

A lightweight, behavioral MOS 6502 emulator written in Python, designed for clarity, testability, and experimentation.
It can serve as a platform for further retro-computing experiments.

![Animation of the WozMon example running](assets/wozmon.svg)

This example shows it running WozMon by exposing the terminal to the CPU as a memory-mapped peripheral.

## Features

**Project maturity:** early but functional.

The following features are **implemented now**:

- Full set of legal / documented NMOS 6502 instructions
- Correct implementation of decimal mode
- Instruction-stepped CPU execution
- Flexible, configurable memory backend
- Clean, testable code architecture
- High test coverage

Currently **still missing** / potentially added later:

- Illegal / undocumented opcodes
- 65C02 features
- Machine language monitor
- Cycle-accurate emulation

## Installation

Install from source:

```bash
git clone https://github.com/florianehmann/another6502
cd another6502
pip install -e .
```

## Examples

For more detailed examples, see the `examples/` directory. There you can find:

- A simple hello world program that prints a message to the terminal from within the 6502
- An echo program that reads characters from the terminal into the 6502 and echoes them back
- WozMon running on the emulated 6502

## Testing

The project includes an extensive test suite covering:

- Instruction behavior
- Flag behavior
- Stack operations
- Addressing modes
- Branching

Run tests with:

```bash
pytest
```

## Limitations

This emulator is **not intended for high-performance emulation**. Not that you would need that for 6502 software, but still, it needs to be said.

Further, it is **not cycle-accurate**. That means you cannot use it to emulate timing-critical applications. For example, it's currently not possible to build an accurate full-system emulator of a Commodore 64 or Nintendo Entertainment System based on this emulator because the software may rely on cycle-accurate timing to coordinate the CPU and other hardware, like the video chip.

Given the previous limitation, this package also **doesn't provide full system emulation**. You can't just load a C64 program, because this package doesn't emulate a full C64, just the 6502 processor.

This project is primarily aimed at:

- Studying retro computing and the 6502 microprocessor
- Experimentation with emulator architecture
- Creating a controlled and observable environment for 6502 software development
- Providing a platform for future experiments

## Contributing

Feedback, issues, and pull requests are welcome!

## License

(TODO license)
