from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import numpy as np
from numpy.typing import NDArray

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_Window = TypeVar("T_Window")
T_Canvas = TypeVar("T_Canvas")


# 构造三视图测试窗口和掩码，供定位、配色及只读验证使用。
class T_ObservationFixtures(ABC, Generic[T_Window, T_Canvas]):
    # 按指定间距读取并重采样医学影像，返回体积接口。
    @abstractmethod
    def load_volume(
        self,
        window: T_Window,
        path: I_FilePath,
        shape: tuple[int, int, int] = (20, 16, 9),
    ) -> None: ...

    # 生成带已知前景位置的掩码，供截面和区间比较使用。
    @abstractmethod
    def seed_masks(self, window: T_Window) -> NDArray[np.uint8]: ...

    # 构造带测试切片的画布，供鼠标交互和显示断言使用。
    @abstractmethod
    def canvas(self, window: T_Window, name: str) -> T_Canvas: ...

    # 提取画布遮罩的前景像素，用于比较显示结果和预期掩码。
    @abstractmethod
    def overlay_mask(self, canvas: T_Canvas) -> NDArray[np.bool_]: ...
