from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import numpy as np
from numpy.typing import NDArray

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_Window = TypeVar("T_Window")
T_Canvas = TypeVar("T_Canvas")


# 构造外置掩码预览窗口，并检查遮罩和界面状态。
class T_ExternalMaskGuiFixtures(ABC, Generic[T_Window, T_Canvas]):
    # 驱动 Qt 事件循环直到后台读取完成，并在超时或失败时终止测试。
    @abstractmethod
    def wait_loaded(self, window: T_Window) -> None: ...

    # 生成可复现的标注样本，供多个测试场景使用。
    @abstractmethod
    def seed(self, window: T_Window) -> None: ...

    # 在测试目录写入掩码，供外置预览加载流程使用。
    @abstractmethod
    def write_mask(
        self,
        window: T_Window,
        tmp_path: I_FilePath,
        suffix: str = ".nii.gz",
        empty: bool = False,
    ) -> tuple[I_FilePath, NDArray[np.uint8]]: ...

    # 查询画布的掩码图层，供测试检查颜色和像素。
    @abstractmethod
    def overlay(self, canvas: T_Canvas) -> NDArray[np.uint8]: ...
