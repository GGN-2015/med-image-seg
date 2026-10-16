from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Generic, TypeVar

import numpy as np
from numpy.typing import NDArray

T_Context = TypeVar("T_Context")
T_Point = TypeVar("T_Point")


# 处理界面锁定、窗宽窗位和十字线点击，隔离 Qt 交互细节。
class T_InteractionService(ABC, Generic[T_Context, T_Point]):
    # 临时禁用主界面、附属窗口和快捷键，在闭合流程结束后恢复原状态。
    @abstractmethod
    def polygon_busy_ui(
        self, context: T_Context, status_key: str = "closing_polygon_status"
    ) -> AbstractContextManager[None]: ...

    # 把截面点击转换为共享体素交点，并同步其余截面的层号。
    @abstractmethod
    def observation_clicked(
        self, context: T_Context, name: str, point: T_Point
    ) -> None: ...

    # 修改指定截面的固定轴坐标，限制到影像范围后同步三个视图。
    @abstractmethod
    def set_observation_axis(
        self, context: T_Context, name: str, index: int
    ) -> None: ...

    # 将当前 LP 层按窗宽窗位转换为显示灰度。
    @abstractmethod
    def windowed_slice(self, context: T_Context) -> NDArray[np.uint8]: ...

    # 将指定截面按当前窗宽窗位转换为显示灰度。
    @abstractmethod
    def windowed_plane(
        self, context: T_Context, plane: NDArray[np.float32]
    ) -> NDArray[np.uint8]: ...
