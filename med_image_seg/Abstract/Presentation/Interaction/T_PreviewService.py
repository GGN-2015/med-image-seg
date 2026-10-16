from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Storage.Paths.I_FilePath import I_FilePath
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_Context = TypeVar("T_Context")


# 协调外置掩码的只读预览，并刷新三个联动截面。
class T_PreviewService(ABC, Generic[T_Context]):
    # 保存编辑状态并进入只读模式，为外置掩码选择和加载做准备。
    @abstractmethod
    def begin_external_preview(self, context: T_Context) -> bool: ...

    # 在后台读取选中的外置掩码，并锁定相关操作直到结果返回。
    @abstractmethod
    def start_external_mask_load(
        self, context: T_Context, path: I_FilePath
    ) -> None: ...

    # 按共享交点刷新 LP、PS、SL 切片、掩码和参考线。
    @abstractmethod
    def refresh_observation_views(self, context: T_Context) -> None: ...
