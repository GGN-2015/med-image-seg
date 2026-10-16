from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Storage.Paths.I_SourcePathRules import I_SourcePathRules

if TYPE_CHECKING:
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final


# 统一影像后缀与配套文件命名，避免标注文件被误判为输入影像。
@final
class C_SourcePathRules(I_SourcePathRules):
    # 排除标注、掩码和已知非 DICOM 文件后判断候选输入。
    def is_dicom_candidate(self, path: I_FilePath) -> bool:
        name = path.getName().lower()
        return (
            path.is_file()
            and (not name.startswith(".med-image-seg.json"))
            and (name not in C_SourcePathRules().getDicomOutputNames())
            and (
                path.getSuffix().lower()
                not in C_SourcePathRules().getNonDicomSuffixes()
            )
        )

    # 移除完整医学影像后缀，确保 .nii.gz 等复合后缀正确生成配套文件名。
    def strip_medical_suffix(self, name: str) -> str:
        from .C_FilePath import C_FilePath

        lower = name.lower()
        for suffix in (".nii.gz", ".ubd.npz", ".nii"):
            if lower.endswith(suffix):
                return name[: -len(suffix)]
        return C_FilePath(name).getStem()

    # 返回不应作为 DICOM 输入的文件后缀。
    def getNonDicomSuffixes(self) -> set[str]:
        return {
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

    # 返回DICOM 目录中的配套输出文件名。
    def getDicomOutputNames(self) -> set[str]:
        return {
            ".med-image-seg.json",
            ".med-image-seg.json.bak",
            ".med-image-seg.json.tmp",
            "med-image-seg-mask.nii.gz",
            "med-image-seg-mask.ubd.npz",
        }
