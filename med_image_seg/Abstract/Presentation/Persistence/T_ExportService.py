from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_Context = TypeVar("T_Context")


# 处理界面导出请求和成功失败提示，把写盘工作交给导出接口。
class T_ExportService(ABC, Generic[T_Context]):
    # 让用户选择导出文件名和目录，并为缺少扩展名的输入补齐目标格式后缀。
    @abstractmethod
    def select_output(
        self,
        context: T_Context,
        suggested_output: I_FilePath,
        title: str,
        file_filter: str,
        required_suffix: str,
    ) -> I_FilePath | None: ...

    # 检查导出条件并执行掩码写入，只在成功后显示完成提示。
    @abstractmethod
    def export_mask(self, context: T_Context, output: I_FilePath) -> None: ...

    # 保存当前项目到用户选择的 JSON 文件，并保留编号空文件删除规则。
    @abstractmethod
    def export_annotations(self, context: T_Context, output: I_FilePath) -> None: ...
