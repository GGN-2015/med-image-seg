"""Public programmable interface for launching the annotation GUI."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from .localization import UiLanguage, normalize_language
from .sources import ImageCollection, ImageSource


@dataclass(slots=True)
class AnnotationApplication:
    """Configure and run an annotation application from Python."""

    spacing_mm: float = 0.8
    language: UiLanguage = "en"
    sources: ImageCollection = field(default_factory=ImageCollection)

    def __post_init__(self) -> None:
        if self.spacing_mm <= 0:
            raise ValueError("spacing_mm must be greater than zero")
        self.language = normalize_language(self.language)

    @classmethod
    def from_paths(
        cls,
        paths: Iterable[str | Path],
        *,
        spacing_mm: float = 0.8,
        language: UiLanguage = "en",
    ) -> AnnotationApplication:
        return cls(
            spacing_mm=spacing_mm,
            language=language,
            sources=ImageCollection(paths),
        )

    def add_image(self, path: str | Path) -> ImageSource:
        return self.sources.add(path)

    def run(self) -> int:
        from .gui import run_annotation_app

        return run_annotation_app(
            sources=list(self.sources),
            spacing_mm=self.spacing_mm,
            language=self.language,
        )


def launch_annotation_app(
    paths: Iterable[str | Path] = (),
    *,
    spacing_mm: float = 0.8,
    language: UiLanguage = "en",
) -> int:
    """Launch the GUI with an optional initial image collection."""

    return AnnotationApplication.from_paths(
        paths,
        spacing_mm=spacing_mm,
        language=language,
    ).run()


__all__ = ["AnnotationApplication", "launch_annotation_app"]
