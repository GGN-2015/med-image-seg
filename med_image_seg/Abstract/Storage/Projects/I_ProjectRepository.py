from __future__ import annotations

from typing import TYPE_CHECKING

from ...Domain.Snapshots.I_RecordSnapshot import I_RecordSnapshot

if TYPE_CHECKING:
    from ...Domain.Annotations.I_MutableAnnotationProject import (
        I_MutableAnnotationProject,
    )
    from ..Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod


# 读取项目或备份并解码旧格式 JSON，恢复轮廓和缺省字段。
class I_ProjectRepository(ABC):
    # 先读取主标注文件，失败时尝试同编号备份；两者都不可读则报告错误。
    @abstractmethod
    def load(self, path: str | I_FilePath) -> I_MutableAnnotationProject: ...

    # 从 JSON 快照恢复项目，补齐旧版缺省字段和历史编辑顺序。
    @abstractmethod
    def decode(self, snapshot: I_RecordSnapshot) -> I_MutableAnnotationProject: ...
