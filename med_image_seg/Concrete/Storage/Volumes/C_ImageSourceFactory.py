from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Domain.Imaging.E_SourceKind import E_SourceKind
from ....Abstract.Storage.Volumes.I_ImageSourceFactory import I_ImageSourceFactory

if TYPE_CHECKING:
    from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final


# 从输入路径识别影像类型，计算指纹并确定配套文件位置。
@final
class C_ImageSourceFactory(I_ImageSourceFactory):
    # 从文件或目录创建影像源，确定类型、指纹及配套输出路径。
    def from_path(self, path: str | I_FilePath) -> I_ImageSource:
        from ...Domain.Imaging.C_ImageSource import C_ImageSource
        from ..Paths.C_FilePath import C_FilePath
        from ..Paths.C_SourceClassifier import C_SourceClassifier
        from ..Paths.C_SourceFingerprint import C_SourceFingerprint
        from ..Paths.C_SourcePathRules import C_SourcePathRules

        source = C_FilePath(path).expanduser().resolve()
        if not source.exists():
            raise FileNotFoundError(f"image source not found: {source}")
        kind, canonical = C_SourceClassifier().classify(source)
        fingerprint = C_SourceFingerprint().fingerprint(canonical, kind)
        if kind == E_SourceKind.DICOM:
            annotation_path = canonical / ".med-image-seg.json"
            mask_path = canonical / "med-image-seg-mask.nii.gz"
        else:
            base = C_SourcePathRules().strip_medical_suffix(canonical.getName())
            annotation_path = canonical.getParent() / f"{base}.med-image-seg.json"
            mask_path = canonical.getParent() / f"{base}.med-image-seg-mask.nii.gz"
        return C_ImageSource(
            path=canonical,
            kind=kind,
            source_id=f"IMAGE-{fingerprint[:12].upper()}",
            fingerprint=fingerprint,
            annotation_path=annotation_path,
            mask_path=mask_path,
        )
