from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Domain.Annotations import (
    I_MutableAnnotationProject,
)
from med_image_seg.Abstract.Domain.Geometry.I_PointList import I_PointList
from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_Window = TypeVar("T_Window")


# 构造多编号项目及写盘样本，供编号切换和删除策略测试使用。
class T_NumberedAnnotationsFixtures(ABC, Generic[T_Window]):
    # 启动影像读取前保存当前项目，避免切换来源时丢失标注。
    @abstractmethod
    def load_source(
        self,
        window: T_Window,
        path: I_FilePath,
        shape: tuple[int, int, int] = (20, 16, 9),
    ) -> I_ImageSource: ...

    # 构造指定位置的轮廓样本，供标注行为测试使用。
    @abstractmethod
    def polygon(self, offset: float = 0) -> I_PointList: ...

    # 使用当前影像和网格创建空项目。
    @abstractmethod
    def new_project(self, window: T_Window) -> I_MutableAnnotationProject: ...

    # 确认外置掩码操作没有生成或修改标注配套文件。
    @abstractmethod
    def assert_no_sidecars(self, path: I_FilePath) -> None: ...
