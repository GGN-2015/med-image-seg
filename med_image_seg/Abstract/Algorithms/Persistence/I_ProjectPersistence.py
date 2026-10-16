from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 原子保存标注并维护备份，按编号策略删除不含多边形的文件。
class I_ProjectPersistence(ABC):
    # 按空文件策略删除或原子替换 JSON，并维护备份以支持异常恢复。
    @abstractmethod
    def save(
        self,
        context: I_MutableAnnotationProject,
        path: str | I_FilePath,
        *,
        delete_if_empty: bool = False,
    ) -> I_FilePath: ...
