"""Echo typed characters back into stdout."""  # noqa: INP001

import sys
import termios
import tty
from queue import Queue
from threading import Thread


def monitor_stdin(input_queue: Queue[bytes | None]) -> None:
    """Set terminal to raw mode and put incoming bytes on stdin into a queue.

    When this function receives a Ctrl+C (0x03) or encounters an exception, it restores the terminal to its
    previous state.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.buffer.read(1)
            if ch == b"\x03":  # Ctrl+C / End of Text
                input_queue.put(None)
                return
            input_queue.put(ch)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    input_queue: Queue[bytes | None] = Queue()
    Thread(target=monitor_stdin, args=(input_queue,)).start()

    while True:
        ch = input_queue.get()
        if ch is None:
            break
        sys.stdout.buffer.write(ch)
        sys.stdout.buffer.flush()
