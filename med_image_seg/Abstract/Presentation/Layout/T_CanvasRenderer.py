from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_Context = TypeVar("T_Context")


# 重绘多边形草稿路径，让画布事件处理不承担路径构造细节。
class T_CanvasRenderer(ABC, Generic[T_Context]):
    # 重建未闭合轮廓的路径图元，使鼠标绘制结果及时显示。
    @abstractmethod
    def update_draft(self, context: T_Context) -> None: ...
