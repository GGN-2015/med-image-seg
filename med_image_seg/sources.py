"""Medical-image source discovery and colocated output paths."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class SourceKind(StrEnum):
    DICOM = "dicom"
    NIFTI = "nifti"
    UBD = "ubd"


_NON_DICOM_SUFFIXES = {
    ".avi",
    ".bak",
    ".bmp",
    ".gif",
    ".gz",
    ".jpeg",
    ".jpg",
    ".json",
    ".mp4",
    ".nii",
    ".npz",
    ".png",
    ".tmp",
}
_DICOM_OUTPUT_NAMES = {
    ".med-image-seg.json",
    ".med-image-seg.json.bak",
    ".med-image-seg.json.tmp",
    "med-image-seg-mask.nii.gz",
}


def _is_dicom_candidate(path: Path) -> bool:
    name = path.name.lower()
    return (
        path.is_file()
        and not name.startswith(".med-image-seg.json")
        and name not in _DICOM_OUTPUT_NAMES
        and path.suffix.lower() not in _NON_DICOM_SUFFIXES
    )


def _strip_medical_suffix(name: str) -> str:
    lower = name.lower()
    for suffix in (".nii.gz", ".ubd.npz", ".nii"):
        if lower.endswith(suffix):
            return name[: -len(suffix)]
    return Path(name).stem


@dataclass(frozen=True, slots=True)
class ImageSource:
    """One loadable image and its colocated annotation/output paths."""

    path: Path
    kind: SourceKind
    source_id: str
    fingerprint: str
    annotation_path: Path
    mask_path: Path

    @classmethod
    def from_path(cls, path: str | Path) -> ImageSource:
        source = Path(path).expanduser().resolve()
        if not source.exists():
            raise FileNotFoundError(f"image source not found: {source}")
        kind, canonical = cls._classify(source)
        fingerprint = cls._fingerprint(canonical, kind)
        if kind == SourceKind.DICOM:
            annotation_path = canonical / ".med-image-seg.json"
            mask_path = canonical / "med-image-seg-mask.nii.gz"
        else:
            base = _strip_medical_suffix(canonical.name)
            annotation_path = canonical.parent / f"{base}.med-image-seg.json"
            mask_path = canonical.parent / f"{base}.med-image-seg-mask.nii.gz"
        return cls(
            path=canonical,
            kind=kind,
            source_id=f"IMAGE-{fingerprint[:12].upper()}",
            fingerprint=fingerprint,
            annotation_path=annotation_path,
            mask_path=mask_path,
        )

    @staticmethod
    def _classify(path: Path) -> tuple[SourceKind, Path]:
        if path.is_dir():
            return SourceKind.DICOM, path
        lower = path.name.lower()
        if lower.endswith((".nii", ".nii.gz")):
            return SourceKind.NIFTI, path
        if lower.endswith(".ubd.npz"):
            return SourceKind.UBD, path
        if lower.endswith(".dcm") or not path.suffix:
            return SourceKind.DICOM, path.parent
        raise ValueError(
            "unsupported image source; expected a DICOM directory/file, "
            ".nii, .nii.gz, or .ubd.npz"
        )

    @staticmethod
    def _fingerprint(path: Path, kind: SourceKind) -> str:
        digest = hashlib.sha256()
        digest.update(kind.value.encode("ascii"))
        if path.is_file():
            stat = path.stat()
            digest.update(path.name.encode("utf-8", errors="surrogatepass"))
            digest.update(str(stat.st_size).encode("ascii"))
            digest.update(str(stat.st_mtime_ns).encode("ascii"))
            with path.open("rb") as handle:
                digest.update(handle.read(1024 * 1024))
            return digest.hexdigest()

        files = sorted(
            (item for item in path.iterdir() if _is_dicom_candidate(item)),
            key=lambda item: item.name,
        )
        if not files:
            raise ValueError(f"DICOM directory contains no candidate files: {path}")
        digest.update(str(len(files)).encode("ascii"))
        for item in files:
            stat = item.stat()
            digest.update(item.name.encode("utf-8", errors="surrogatepass"))
            digest.update(str(stat.st_size).encode("ascii"))
        for item in dict.fromkeys((files[0], files[len(files) // 2], files[-1])):
            with item.open("rb") as handle:
                digest.update(handle.read(1024 * 1024))
        return digest.hexdigest()

    @property
    def display_name(self) -> str:
        if self.kind == SourceKind.DICOM:
            label = self.path.name
            count = sum(_is_dicom_candidate(item) for item in self.path.iterdir())
            return f"[DICOM] {label}  |  {count} files"
        return f"[{self.kind.value.upper()}] {self.path.name}"


class ImageCollection:
    """Ordered, deduplicated collection used by the GUI and CLI."""

    def __init__(self, sources: Iterable[str | Path | ImageSource] = ()) -> None:
        self._sources: list[ImageSource] = []
        self._by_fingerprint: dict[str, ImageSource] = {}
        self.extend(sources)

    def add(self, source: str | Path | ImageSource) -> ImageSource:
        item = (
            source if isinstance(source, ImageSource) else ImageSource.from_path(source)
        )
        existing = self._by_fingerprint.get(item.fingerprint)
        if existing is not None:
            return existing
        self._sources.append(item)
        self._by_fingerprint[item.fingerprint] = item
        return item

    def extend(self, sources: Iterable[str | Path | ImageSource]) -> None:
        for source in sources:
            self.add(source)

    def __len__(self) -> int:
        return len(self._sources)

    def __iter__(self):
        return iter(self._sources)

    def __getitem__(self, index: int) -> ImageSource:
        return self._sources[index]


__all__ = ["ImageCollection", "ImageSource", "SourceKind"]
