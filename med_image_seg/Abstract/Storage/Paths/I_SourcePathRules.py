from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 统一影像后缀与配套文件命名，避免标注文件被误判为输入影像。
class I_SourcePathRules(ABC):
    # 排除标注、掩码和已知非 DICOM 文件后判断候选输入。
    @abstractmethod
    def is_dicom_candidate(self, path: I_FilePath) -> bool: ...

    # 移除完整医学影像后缀，确保 .nii.gz 等复合后缀正确生成配套文件名。
    @abstractmethod
    def strip_medical_suffix(self, name: str) -> str: ...

    # 返回不应作为 DICOM 输入的文件后缀。
    @abstractmethod
    def getNonDicomSuffixes(self) -> set[str]: ...

    # 返回DICOM 目录中的配套输出文件名。
    @abstractmethod
    def getDicomOutputNames(self) -> set[str]: ...
