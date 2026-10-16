from __future__ import annotations

from typing import TYPE_CHECKING

from ....Abstract.Domain.Imaging.E_SourceKind import E_SourceKind
from ....Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
from ....Abstract.Domain.Records.I_RecordFieldList import I_RecordFieldList
from ....Abstract.Storage.Paths.I_FilePath import I_FilePath

if TYPE_CHECKING:
    from ....Abstract.Storage.Paths.I_FilePath import I_FilePath
import operator
from dataclasses import dataclass
from typing import final


# 描述影像来源及配套文件路径，用指纹关联影像与标注项目。
@final
@dataclass(slots=True, frozen=True, init=False)
class C_ImageSource(I_ImageSource):
    _state_path: I_FilePath
    _state_kind: E_SourceKind
    _state_source_id: str
    _state_fingerprint: str
    _state_annotation_path: I_FilePath
    _state_mask_path: I_FilePath

    # 保存影像类型、指纹和配套标注及掩码路径。
    def __init__(
        self,
        path: I_FilePath,
        kind: E_SourceKind,
        source_id: str,
        fingerprint: str,
        annotation_path: I_FilePath,
        mask_path: I_FilePath,
    ) -> None:
        from ...Storage.Paths.C_FilePath import C_FilePath

        object.__setattr__(self, "_state_path", C_FilePath(path))
        object.__setattr__(self, "_state_kind", kind)
        object.__setattr__(self, "_state_source_id", source_id)
        object.__setattr__(self, "_state_fingerprint", fingerprint)
        object.__setattr__(self, "_state_annotation_path", C_FilePath(annotation_path))
        object.__setattr__(self, "_state_mask_path", C_FilePath(mask_path))

    # 返回影像输入路径。
    def getPath(self) -> I_FilePath:
        return self._state_path

    # 返回影像的 DICOM、NIfTI 或 UBD 格式类别。
    def getKind(self) -> E_SourceKind:
        return self._state_kind

    # 返回影像来源标识。
    def getSourceId(self) -> str:
        return self._state_source_id

    # 返回不包含标注输出文件的影像指纹。
    def getFingerprint(self) -> str:
        return self._state_fingerprint

    # 返回影像旁的默认标注路径。
    def getAnnotationPath(self) -> I_FilePath:
        return self._state_annotation_path

    # 返回NIfTI 掩码输出路径。
    def getMaskPath(self) -> I_FilePath:
        return self._state_mask_path

    # 返回有序的记录字段名，供序列化读取。
    def getRecordFields(self) -> I_RecordFieldList:
        from ..Records.C_RecordFieldList import C_RecordFieldList

        return C_RecordFieldList(
            ("path", "kind", "source_id", "fingerprint", "annotation_path", "mask_path")
        )

    # 返回UBD 掩码输出路径。
    def getUbdMaskPath(self) -> I_FilePath:
        from ...Storage.Paths.C_SourcePathRules import C_SourcePathRules

        base = C_SourcePathRules().strip_medical_suffix(self.getMaskPath().getName())
        return self.getMaskPath().with_name(f"{base}.ubd.npz")

    # 按编号生成标注路径：0 号保留原名，其余使用数字后缀。
    def annotation_path_for_index(self, index: int) -> I_FilePath:
        index = operator.index(index)
        if index < 0:
            raise ValueError("annotation index must be nonnegative")
        if index == 0:
            return self.getAnnotationPath()
        return self.getAnnotationPath().with_name(
            f"{self.getAnnotationPath().getStem()}-{index}.json"
        )

    # 返回影像列表中的显示名称。
    def getDisplayName(self) -> str:
        from ...Storage.Paths.C_SourcePathRules import C_SourcePathRules

        if self.getKind() == E_SourceKind.DICOM:
            label = self.getPath().getName()
            count = sum(
                C_SourcePathRules().is_dicom_candidate(item)
                for item in self.getPath().iterdir()
            )
            return f"[DICOM] {label}  |  {count} files"
        return f"[{self.getKind().value.upper()}] {self.getPath().getName()}"
