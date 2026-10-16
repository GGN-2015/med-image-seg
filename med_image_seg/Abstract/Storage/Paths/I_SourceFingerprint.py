from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Imaging.E_SourceKind import E_SourceKind
    from .I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 以影像文件信息生成稳定指纹，排除软件生成的标注和掩码文件。
class I_SourceFingerprint(ABC):
    # 对输入影像文件信息计算摘要，忽略软件生成的标注和掩码输出。
    @abstractmethod
    def fingerprint(self, path: I_FilePath, kind: E_SourceKind) -> str: ...
