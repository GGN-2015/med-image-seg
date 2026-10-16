from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Imaging.E_SourceKind import E_SourceKind
    from .I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 根据目录和文件后缀识别 DICOM、NIfTI 或 UBD 影像来源。
class I_SourceClassifier(ABC):
    # 根据输入是目录还是支持的文件后缀识别影像类型。
    @abstractmethod
    def classify(self, path: I_FilePath) -> tuple[E_SourceKind, I_FilePath]: ...
