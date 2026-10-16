from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_Context = TypeVar("T_Context")


# 处理界面导出请求和成功失败提示，把写盘工作交给导出接口。
class T_ExportService(ABC, Generic[T_Context]):
    # 检查导出条件并执行掩码写入，只在成功后显示完成提示。
    @abstractmethod
    def export_mask(self, context: T_Context, output: I_FilePath) -> None: ...
