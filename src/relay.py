import serial
import threading

from queue import Queue, Empty


ser = None
incoming = Queue()


def connect(port: str, baudrate: int = 115200, timeout: float = 1.0) -> None:
    global ser

    ser = serial.serial_for_url(
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
    assert ser is not None, "Connection not valid."

    while True:
        if ser.in_waiting:
            message = ser.readline().decode("utf-8").strip()

            if message:
                incoming.put(message)


def send(message: str) -> None:
    assert ser is not None, "Connection not valid."

    ser.write((message + "\n").encode("utf-8"))


def read() -> str | None:
    try:
        return incoming.get_nowait()
    except Empty:
        return None


def close() -> None:
    assert ser is not None, "Connection not valid."

    ser.close()