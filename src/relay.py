import threading
from queue import Queue, Empty
import serial



SER = None
incoming = Queue()


def connect(port: str, baudrate: int = 115200, timeout: float = 1.0) -> None:
    global SER

    SER = serial.serial_for_url(
        port,
        baudrate=baudrate,
        timeout=timeout
    )

    thread = threading.Thread(
        target=_reader,
        daemon=True
    )

    thread.start()


def _reader() -> None:
    assert SER is not None, "Connection not valid."

    while True:
        if SER.in_waiting:
            message = SER.readline().decode("utf-8").strip()

            if message:
                incoming.put(message)


def send(message: str) -> None:
    assert SER is not None, "Connection not valid."

    SER.write((message + "\n").encode("utf-8"))


def read() -> str | None:
    try:
        return incoming.get_nowait()
    except Empty:
        return None


def close() -> None:
    assert SER is not None, "Connection not valid."

    SER.close()