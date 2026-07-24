import threading
import queue
import time

import relay


commands = queue.Queue()


def terminal() -> None:
    while True:
        command = input("> ")

        commands.put(command)

        if command == "quit":
            break


def main():
    relay.connect("loop://", 115200, 1.0)
    # relay.connect("/dev/ttyV0", 115200, 1.0)

    terminal_thread = threading.Thread(
        target=terminal,
        daemon=True
    )

    terminal_thread.start()

    while True:
        # Handle terminal commands
        try:
            command = commands.get_nowait()

            if command == "quit":
                break

            relay.send(command)

        except queue.Empty:
            pass


        # Handle incoming serial messages
        response = relay.read()

        if response is not None:
            print(response)


        time.sleep(0.01)


    relay.close()


if __name__ == "__main__":
    main()