import math
import time
import numpy as np
import pyvista as pv
from parser import Point

pv.global_theme.allow_empty_mesh = True

def spherical_to_cartesian(point: Point) -> np.ndarray:
    distance_metres = point.distance

    azimuth_radians = math.radians(point.azimuth)
    elevation_radians = math.radians(point.elevation)

    z = distance_metres * math.sin(elevation_radians)
    y = distance_metres * math.cos(elevation_radians) * math.sin(azimuth_radians)
    x = distance_metres * math.cos(elevation_radians) * math.cos(azimuth_radians)

    return np.array([x, y, z])

class Viewer:
    def __init__(self, max_points: int = 100_000, max_render_fps: float = 60.0):
        self.max_points = max_points
        self.max_render_interval = 1.0 / max_render_fps
        self._buffer = np.empty((max_points, 3), dtype=np.float32)
        self._size = 0
        self._head = 0
        self._dirty = False
        self._last_render = 0.0

        self.plotter = pv.Plotter()
        self.plotter.set_background("#281f1f")
        self.plotter.show_axes()
        self.plotter.enable_terrain_style()
        self.plotter.enable_lightkit()
        
        self.plotter.camera_position = [
            (600, 600, 400),
            (0, 0, 0),
            (0, 0, 1)
        ]

        self.plotter.camera.zoom(1.3)
        self.plotter.camera.SetViewAngle(30)
        self.plotter.camera.clipping_range = (1e-12, 1e12)

        origin = pv.PolyData(np.array([[0, 0, 0]], dtype=np.float32))

        self.plotter.add_mesh(
            origin,
            color="red",
            point_size=10,
            render_points_as_spheres=True
        )

        self.points = pv.PolyData(np.empty((0, 3), dtype=np.float32))

        self.actor = self.plotter.add_mesh(
            self.points,
            color="#d13c21",
            point_size=5,
            render_points_as_spheres=False
        )

        grid = pv.Plane(
            center=(0, 0, 0),
            direction=(0, 0, 1),
            i_size=1600,
            j_size=1600,
            i_resolution=20,
            j_resolution=20
        )

        self.plotter.add_mesh(
            grid,
            style="wireframe",
            color="#1e0805",
            line_width=1,
        )


    def add_points(self, points: np.ndarray) -> None:
        points = np.asarray(points, dtype=np.float32).reshape(-1, 3)

        if points.size == 0:
            return

        if len(points) >= self.max_points:
            points = points[-self.max_points :]
            self._buffer[: len(points)] = points
            self._size = len(points)
            self._head = 0
            self._dirty = True
            return

        write_count = len(points)
        tail_capacity = self.max_points - self._head

        if write_count <= tail_capacity:
            self._buffer[self._head : self._head + write_count] = points
        else:
            self._buffer[self._head :] = points[:tail_capacity]
            remaining = write_count - tail_capacity
            self._buffer[:remaining] = points[tail_capacity:]

        self._head = (self._head + write_count) % self.max_points
        self._size = min(self.max_points, self._size + write_count)
        self._dirty = True

    def _view_points(self) -> np.ndarray:
        if self._size == 0:
            return self._buffer[:0]

        if self._size < self.max_points:
            return self._buffer[: self._size]

        return self._buffer

    def render(self, force: bool = False) -> None:
        now = time.monotonic()

        if self._dirty and (force or now - self._last_render >= self.max_render_interval):
            self.actor.mapper.dataset.copy_from(
                pv.PolyData(self._view_points().copy())
            )
            self._dirty = False
            self._last_render = now
            self.plotter.update(stime=1, force_redraw=True)
            return

        self.plotter.update(stime=1, force_redraw=False)

    def show(self):
        self.plotter.show(auto_close=False, interactive_update=True)