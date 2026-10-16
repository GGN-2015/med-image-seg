from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Domain.Imaging.E_SourceKind import E_SourceKind
from ....Abstract.Storage.Paths.I_SourceClassifier import I_SourceClassifier

if TYPE_CHECKING:
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final


# 根据目录和文件后缀识别 DICOM、NIfTI 或 UBD 影像来源。
@final
class C_SourceClassifier(I_SourceClassifier):
    # 根据输入是目录还是支持的文件后缀识别影像类型。
    def classify(self, path: I_FilePath) -> tuple[E_SourceKind, I_FilePath]:
        if path.is_dir():
            return (E_SourceKind.DICOM, path)
        lower = path.getName().lower()
        if lower.endswith((".nii", ".nii.gz")):
            return (E_SourceKind.NIFTI, path)
        if lower.endswith(".ubd.npz"):
            return (E_SourceKind.UBD, path)
        if lower.endswith(".dcm") or not path.getSuffix():
            return (E_SourceKind.DICOM, path.getParent())
        raise ValueError(
            "unsupported image source; expected a DICOM directory/file,"
            " .nii, .nii.gz, or .ubd.npz"
        )
