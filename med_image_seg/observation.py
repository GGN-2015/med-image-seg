"""Orthogonal views on the volume's L/P/S voxel grid."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class ObservationPlane:
    name: str
    horizontal_axis: int
    vertical_axis: int
    fixed_axis: int
    color: str

    def section(self, data: np.ndarray, position: tuple[int, int, int]) -> np.ndarray:
        selection: list[slice | int] = [slice(None), slice(None), slice(None)]
        selection[self.fixed_axis] = position[self.fixed_axis]
        section = data[tuple(selection)]
        remaining_axes = [axis for axis in range(3) if axis != self.fixed_axis]
        if remaining_axes == [self.vertical_axis, self.horizontal_axis]:
            return section
        return section.T

    def position_at(
        self,
        position: tuple[int, int, int],
        horizontal: float,
        vertical: float,
        shape: tuple[int, int, int],
    ) -> tuple[int, int, int]:
        updated = list(position)
        for axis, coordinate in (
            (self.horizontal_axis, horizontal),
            (self.vertical_axis, vertical),
        ):
            updated[axis] = int(np.clip(np.floor(coordinate), 0, shape[axis] - 1))
        return tuple(updated)


OBSERVATION_PLANES = {
    "LP": ObservationPlane("LP", 0, 1, 2, "#00ffff"),
    "PS": ObservationPlane("PS", 1, 2, 0, "#ff00ff"),
    "SL": ObservationPlane("SL", 2, 0, 1, "#ffff00"),
}

AXIS_COLORS = {plane.fixed_axis: plane.color for plane in OBSERVATION_PLANES.values()}
