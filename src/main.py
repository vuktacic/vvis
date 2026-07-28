import threading
import queue
import numpy as np

import parser
import relay
import viewer

commands = queue.Queue()
points = queue.Queue()
view = viewer.Viewer()

def terminal() -> None:
    while True:
        command = input("> ")

        commands.put(command)

        if command == "quit":
            break

def point_processor() -> None:
    # relay.connect("loop://", 115200, 1.0)
    relay.connect("/dev/ttyUSB0", 115200, 1.0)

    while True:
        response = relay.read()

        if response and response.startswith("scan_data"):
            point = parser.parse(response)

            if point is not None:
                points.put(point)
        elif response is not None:
            print(response)


def main():
    view.show()

    processor = threading.Thread(
        target=point_processor,
        daemon=True
    )
    processor.start()

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

        try:
            first_point = points.get(timeout=0.01)
        except queue.Empty:
            first_point = None

        if first_point is not None:
            batch = [first_point]

            while True:
                try:
                    batch.append(points.get_nowait())
                except queue.Empty:
                    break

            cartesian_points = np.asarray(
                [viewer.spherical_to_cartesian(point) for point in batch],
                dtype=np.float32,
            )

            view.add_points(cartesian_points)

        view.render()


    relay.close()


if __name__ == "__main__":
    main()
