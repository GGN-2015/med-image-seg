"""Reusable medical-image polygon annotation application."""

from .annotation import (
    AnnotationExporter,
    AnnotationProject,
    PolygonAnnotation,
    SliceAnnotation,
)
from .application import AnnotationApplication, launch_annotation_app
from .gui import AnnotationMainWindow, SliceCanvas, VolumeLoadThread
from .io import (
    MedicalMaskWriter,
    MedicalVolume,
    MedicalVolumeReader,
    load_volume,
    save_mask,
)
from .sources import ImageCollection, ImageSource, SourceKind

__all__ = [
    "AnnotationApplication",
    "AnnotationExporter",
    "AnnotationMainWindow",
    "AnnotationProject",
    "ImageCollection",
    "ImageSource",
    "MedicalMaskWriter",
    "MedicalVolume",
    "MedicalVolumeReader",
    "PolygonAnnotation",
    "SliceAnnotation",
    "SliceCanvas",
    "SourceKind",
    "VolumeLoadThread",
    "launch_annotation_app",
    "load_volume",
    "save_mask",
]

__version__ = "0.1.0"
