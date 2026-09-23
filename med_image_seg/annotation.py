"""Persistent polygon annotations, interpolation, and mask export."""

from __future__ import annotations

import json
import os
import shutil
from dataclasses import asdict, dataclass, field, replace
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Literal

import numpy as np
from scipy.ndimage import distance_transform_edt
from skimage.draw import polygon as rasterize_polygon

from .io import MedicalMaskWriter, MedicalVolume

PolygonOperation = Literal["add", "erase"]
PolygonSource = Literal["manual", "prototype"]


@dataclass(frozen=True, slots=True)
class PolygonAnnotation:
    """One polygon in displayed axial coordinates (x=L, y=P)."""

    points: tuple[tuple[float, float], ...]
    operation: PolygonOperation = "add"
    source: PolygonSource = "manual"
    edit_order: int = 0

    def __post_init__(self) -> None:
        if self.operation not in ("add", "erase"):
            raise ValueError("operation must be 'add' or 'erase'")
        if self.source not in ("manual", "prototype"):
            raise ValueError("source must be 'manual' or 'prototype'")
        if len(self.points) < 3:
            raise ValueError("a polygon needs at least three points")
        if not all(np.isfinite(point).all() for point in map(np.asarray, self.points)):
            raise ValueError("polygon points must be finite")
        if self.edit_order < 0:
            raise ValueError("edit_order must not be negative")


@dataclass(slots=True)
class SliceAnnotation:
    polygons: list[PolygonAnnotation] = field(default_factory=list)
    completed: bool = False
    keyframe: bool = False
    force_empty: bool = False


@dataclass(slots=True)
class AnnotationProject:
    """Autosavable annotation state for one canonical LPS volume."""

    image_id: str
    source_fingerprint: str
    shape_lps: tuple[int, int, int]
    spacing_lps_mm: tuple[float, float, float]
    origin_lps_mm: tuple[float, float, float]
    slices: dict[int, SliceAnnotation] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)
    edit_counter: int = 0
    schema_version: int = 4
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @classmethod
    def create(
        cls,
        *,
        image_id: str,
        source_fingerprint: str,
        volume: MedicalVolume,
    ) -> AnnotationProject:
        return cls(
            image_id=image_id,
            source_fingerprint=source_fingerprint,
            shape_lps=tuple(int(value) for value in volume.data.shape),
            spacing_lps_mm=volume.spacing_mm,
            origin_lps_mm=volume.origin_lps_mm,
        )

    @classmethod
    def load(cls, path: str | Path) -> AnnotationProject:
        source = Path(path).expanduser().resolve()
        backup = Path(f"{source}.bak")
        errors: list[Exception] = []
        for candidate in (source, backup):
            if not candidate.is_file():
                continue
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
                return cls._from_payload(payload)
            except (OSError, KeyError, TypeError, ValueError) as exc:
                errors.append(exc)
        if errors:
            raise ValueError(
                f"annotation project and backup are unreadable: {source}"
            ) from errors[0]
        raise FileNotFoundError(f"annotation project not found: {source}")

    @classmethod
    def _from_payload(cls, payload: dict) -> AnnotationProject:
        fallback_order = 0
        slices: dict[int, SliceAnnotation] = {}
        for index, annotation in payload.get("slices", {}).items():
            polygons = []
            for polygon in annotation.get("polygons", []):
                fallback_order += 1
                polygons.append(
                    PolygonAnnotation(
                        points=tuple(
                            tuple(map(float, point)) for point in polygon["points"]
                        ),
                        operation=polygon.get("operation", "add"),
                        source=polygon.get("source", "manual"),
                        edit_order=int(polygon.get("edit_order", fallback_order)),
                    )
                )
            slices[int(index)] = SliceAnnotation(
                polygons=polygons,
                completed=bool(annotation.get("completed", False)),
                keyframe=bool(annotation.get("keyframe", False)),
                force_empty=bool(annotation.get("force_empty", False)),
            )
        maximum_order = max(
            (
                polygon.edit_order
                for annotation in slices.values()
                for polygon in annotation.polygons
            ),
            default=0,
        )
        return cls(
            image_id=payload.get("image_id", payload.get("series_id", "IMAGE")),
            source_fingerprint=payload["source_fingerprint"],
            shape_lps=tuple(payload["shape_lps"]),
            spacing_lps_mm=tuple(payload["spacing_lps_mm"]),
            origin_lps_mm=tuple(payload["origin_lps_mm"]),
            slices=slices,
            metadata=dict(payload.get("metadata", {})),
            edit_counter=max(int(payload.get("edit_counter", 0)), maximum_order),
            schema_version=int(payload.get("schema_version", 1)),
            updated_at=payload.get("updated_at", datetime.now(UTC).isoformat()),
        )

    def validate_volume(self, volume: MedicalVolume) -> None:
        if tuple(volume.data.shape) != self.shape_lps:
            raise ValueError("annotation shape does not match the loaded volume")
        if not np.allclose(volume.spacing_mm, self.spacing_lps_mm):
            raise ValueError("annotation spacing does not match the loaded volume")
        if not np.allclose(volume.origin_lps_mm, self.origin_lps_mm):
            raise ValueError("annotation origin does not match the loaded volume")

    def annotation(self, slice_index: int) -> SliceAnnotation:
        if not 0 <= slice_index < self.shape_lps[2]:
            raise IndexError("slice_index is outside the volume")
        return self.slices.setdefault(slice_index, SliceAnnotation())

    def _next_edit_order(self) -> int:
        self.edit_counter += 1
        return self.edit_counter

    def add_polygon(self, slice_index: int, polygon: PolygonAnnotation) -> None:
        annotation = self.annotation(slice_index)
        annotation.force_empty = False
        annotation.polygons.append(replace(polygon, edit_order=self._next_edit_order()))

    def replace_polygon(
        self,
        slice_index: int,
        polygon_index: int,
        points: tuple[tuple[float, float], ...],
    ) -> None:
        annotation = self.annotation(slice_index)
        annotation.force_empty = False
        previous = annotation.polygons[polygon_index]
        annotation.polygons[polygon_index] = PolygonAnnotation(
            points=points,
            operation=previous.operation,
            source="manual",
            edit_order=self._next_edit_order(),
        )

    def delete_last_edited_polygon(
        self,
        slice_index: int,
    ) -> PolygonAnnotation | None:
        """Delete the polygon most recently added or vertex-edited on this slice."""

        polygons = self.annotation(slice_index).polygons
        if not polygons:
            return None
        polygon_index = max(
            range(len(polygons)),
            key=lambda index: polygons[index].edit_order,
        )
        return polygons.pop(polygon_index)

    def copy_slice(self, source_index: int, target_index: int) -> None:
        source = self.annotation(source_index)
        target = self.annotation(target_index)
        target.polygons = [
            replace(
                polygon,
                source="manual",
                edit_order=self._next_edit_order(),
            )
            for polygon in source.polygons
        ]
        target.completed = False
        target.force_empty = False

    def set_completed(self, slice_index: int, completed: bool) -> None:
        annotation = self.annotation(slice_index)
        annotation.completed = bool(completed)
        if completed:
            annotation.keyframe = True

    def set_force_empty(self, slice_index: int, force_empty: bool) -> None:
        """Force one slice to remain empty without deleting stored polygons."""

        self.annotation(slice_index).force_empty = bool(force_empty)

    def set_keyframe(self, slice_index: int, keyframe: bool) -> None:
        self.annotation(slice_index).keyframe = bool(keyframe)

    def clear_slice(self, slice_index: int) -> None:
        if not 0 <= slice_index < self.shape_lps[2]:
            raise IndexError("slice_index is outside the volume")
        self.slices.pop(slice_index, None)

    @property
    def completed_count(self) -> int:
        return sum(annotation.completed for annotation in self.slices.values())

    @property
    def keyframe_indices(self) -> tuple[int, ...]:
        return tuple(
            sorted(
                index
                for index, annotation in self.slices.items()
                if annotation.polygons
                or annotation.keyframe
                or annotation.completed
                or annotation.force_empty
            )
        )

    @property
    def interpolated_slice_count(self) -> int:
        return sum(
            1
            for left, right in pairwise(self.keyframe_indices)
            for index in range(left + 1, right)
            if not self.slices.get(index, SliceAnnotation()).polygons
            and not self.slices.get(index, SliceAnnotation()).completed
            and not self.slices.get(index, SliceAnnotation()).force_empty
        )

    def _manual_plane(self, slice_index: int) -> np.ndarray:
        plane_shape = (self.shape_lps[1], self.shape_lps[0])
        annotation = self.slices.get(slice_index, SliceAnnotation())
        if annotation.force_empty:
            return np.zeros(plane_shape, dtype=bool)
        source_planes = {
            "manual": np.zeros(plane_shape, dtype=bool),
            "prototype": np.zeros(plane_shape, dtype=bool),
        }
        for item in annotation.polygons:
            x = np.asarray([point[0] for point in item.points], dtype=np.float64)
            y = np.asarray([point[1] for point in item.points], dtype=np.float64)
            rows, columns = rasterize_polygon(y, x, shape=plane_shape)
            source_planes[item.source][rows, columns] = item.operation == "add"
        return source_planes["manual"] | source_planes["prototype"]

    @staticmethod
    def _signed_distance(plane: np.ndarray) -> np.ndarray:
        diagonal = float(np.hypot(*plane.shape))
        if not plane.any():
            return np.full(plane.shape, -diagonal, dtype=np.float32)
        if plane.all():
            return np.full(plane.shape, diagonal, dtype=np.float32)
        inside = distance_transform_edt(plane)
        outside = distance_transform_edt(~plane)
        return np.asarray(inside - outside, dtype=np.float32)

    def interpolation_bounds(self, slice_index: int) -> tuple[int, int] | None:
        annotation = self.slices.get(slice_index, SliceAnnotation())
        if (
            annotation.polygons
            or annotation.keyframe
            or annotation.completed
            or annotation.force_empty
        ):
            return None
        keyframes = np.asarray(self.keyframe_indices, dtype=np.int64)
        position = int(np.searchsorted(keyframes, slice_index))
        if position == 0 or position == keyframes.size:
            return None
        return int(keyframes[position - 1]), int(keyframes[position])

    def interpolated_plane(self, slice_index: int) -> np.ndarray | None:
        bounds = self.interpolation_bounds(slice_index)
        if bounds is None:
            return None
        left, right = bounds
        fraction = (slice_index - left) / (right - left)
        left_distance = self._signed_distance(self._manual_plane(left))
        right_distance = self._signed_distance(self._manual_plane(right))
        blended = (1.0 - fraction) * left_distance + fraction * right_distance
        return blended >= 0.0

    def to_mask(self, *, interpolate: bool = True) -> np.ndarray:
        mask = np.zeros(self.shape_lps, dtype=np.uint8)
        for slice_index, annotation in self.slices.items():
            if (
                annotation.polygons or annotation.completed
            ) and not annotation.force_empty:
                mask[:, :, slice_index] = self._manual_plane(slice_index).T
        if not interpolate:
            return mask
        for left, right in pairwise(self.keyframe_indices):
            if right <= left + 1:
                continue
            left_distance = self._signed_distance(self._manual_plane(left))
            right_distance = self._signed_distance(self._manual_plane(right))
            interval = right - left
            for slice_index in range(left + 1, right):
                annotation = self.slices.get(slice_index, SliceAnnotation())
                if (
                    annotation.polygons
                    or annotation.completed
                    or annotation.force_empty
                ):
                    continue
                fraction = (slice_index - left) / interval
                blended = (1.0 - fraction) * left_distance + fraction * right_distance
                mask[:, :, slice_index] = (blended >= 0.0).T
        return mask

    def save(self, path: str | Path) -> Path:
        output = Path(path).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        self.updated_at = datetime.now(UTC).isoformat()
        payload = {
            "schema_version": self.schema_version,
            "image_id": self.image_id,
            "source_fingerprint": self.source_fingerprint,
            "shape_lps": self.shape_lps,
            "spacing_lps_mm": self.spacing_lps_mm,
            "origin_lps_mm": self.origin_lps_mm,
            "updated_at": self.updated_at,
            "edit_counter": self.edit_counter,
            "metadata": self.metadata,
            "slices": {
                str(index): {
                    "completed": annotation.completed,
                    "keyframe": annotation.keyframe,
                    "force_empty": annotation.force_empty,
                    "polygons": [asdict(polygon) for polygon in annotation.polygons],
                }
                for index, annotation in sorted(self.slices.items())
                if annotation.polygons
                or annotation.completed
                or annotation.keyframe
                or annotation.force_empty
            },
        }
        temporary = Path(f"{output}.tmp")
        backup = Path(f"{output}.bak")
        backup_temporary = Path(f"{backup}.tmp")
        serialized = json.dumps(payload, indent=2, ensure_ascii=False)
        try:
            with temporary.open("w", encoding="utf-8") as handle:
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            if output.is_file():
                try:
                    json.loads(output.read_text(encoding="utf-8"))
                except (OSError, TypeError, ValueError):
                    pass
                else:
                    shutil.copy2(output, backup_temporary)
                    os.replace(backup_temporary, backup)
            os.replace(temporary, output)
        finally:
            temporary.unlink(missing_ok=True)
            backup_temporary.unlink(missing_ok=True)
        return output


class AnnotationExporter:
    """Convert a project into a geometry-preserving 3-D mask."""

    def __init__(self, writer: MedicalMaskWriter | None = None) -> None:
        self.writer = writer or MedicalMaskWriter()

    def export(
        self,
        project: AnnotationProject,
        volume: MedicalVolume,
        output_path: str | Path,
        *,
        interpolate: bool = True,
    ) -> Path:
        project.validate_volume(volume)
        return self.writer.write(
            output_path,
            project.to_mask(interpolate=interpolate),
            volume,
        )


__all__ = [
    "AnnotationExporter",
    "AnnotationProject",
    "PolygonAnnotation",
    "PolygonOperation",
    "PolygonSource",
    "SliceAnnotation",
]
