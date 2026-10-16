from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_Application = TypeVar("T_Application")
T_Window = TypeVar("T_Window")


# 构造区间条测试窗口，并生成带关键层的标注样本。
class T_MaskCoverageFixtures(ABC, Generic[T_Application, T_Window]):
    # 复用或创建 QApplication，供测试驱动界面事件。
    @abstractmethod
    def app(self) -> T_Application: ...

    # 启动影像读取前保存当前项目，避免切换来源时丢失标注。
    @abstractmethod
    def load_source(self, window: T_Window, path: I_FilePath) -> I_ImageSource: ...
