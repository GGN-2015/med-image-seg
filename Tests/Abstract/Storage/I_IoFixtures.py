from __future__ import annotations

from abc import ABC, abstractmethod

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath


# 生成测试 DICOM 和 NIfTI 文件，集中管理格式库的测试适配。
class I_IoFixtures(ABC):
    # 生成已知体素及物理几何的 NIfTI 测试文件。
    @abstractmethod
    def write_test_nifti(self, path: I_FilePath) -> None: ...

    # 生成带完整几何标签的 DICOM 测试序列。
    @abstractmethod
    def write_test_dicom_series(self, directory: I_FilePath) -> None: ...
