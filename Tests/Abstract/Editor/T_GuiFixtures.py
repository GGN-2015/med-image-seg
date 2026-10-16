from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource
from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_Application = TypeVar("T_Application")
T_Window = TypeVar("T_Window")


# 构造界面测试的影像与窗口，并驱动后台加载和事件循环。
class T_GuiFixtures(ABC, Generic[T_Application, T_Window]):
    # 复用或创建 QApplication，供测试驱动界面事件。
    @abstractmethod
    def app(self) -> T_Application: ...

    # 创建临时影像源，统一测试项目的配套文件路径和指纹。
    @abstractmethod
    def source(self, tmp_path: I_FilePath) -> I_ImageSource: ...

    # 构造与测试影像源对应的体素和几何信息。
    @abstractmethod
    def volume(self, source: I_ImageSource) -> I_MedicalVolume: ...

    # 写入具有已知几何的 NIfTI 测试影像。
    @abstractmethod
    def write_nifti(self, path: I_FilePath) -> None: ...

    # 断言闭合计算期间编辑控件和快捷键均被禁用。
    @abstractmethod
    def assert_polygon_busy(self, window: T_Window) -> None: ...
