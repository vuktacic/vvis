from dataclasses import dataclass

@dataclass
class Point:
    distance: float
    azimuth: float
    elevation: float


def parse(data: str) -> Point | None:
    try:
        if data.startswith("scan_data"):
            distance, azimuth, elevation = map(float, data.split()[1:4])

            return Point(
                distance = float(distance),
                azimuth = float(azimuth),
                elevation = float(elevation)
            )

    except ValueError:
        return None

    return None