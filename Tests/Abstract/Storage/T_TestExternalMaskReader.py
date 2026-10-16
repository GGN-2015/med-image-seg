from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import numpy as np
from numpy.typing import NDArray

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 验证外置掩码的物理对齐、格式校验和中文路径读取。
class T_TestExternalMaskReader(ABC, Generic[T_MonkeyPatch]):
    # 往返读写外置掩码，验证体素与参考影像网格一致。
    @abstractmethod
    def test_external_mask_round_trip_matches_reference_grid(
        self, tmp_path: I_FilePath, suffix: str, empty: bool
    ) -> None: ...

    # 验证外置掩码的所有非零标签均作为前景显示。
    @abstractmethod
    def test_external_mask_keeps_all_nonzero_labels(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 改变掩码间距及原点，核验最近邻重采样使用物理坐标。
    @abstractmethod
    def test_nifti_resamples_nearest_neighbor_using_physical_origin_and_spacing(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 翻转 NIfTI 方向，核验读取结果正确重定向到 LPS。
    @abstractmethod
    def test_nifti_direction_flip_is_correctly_reoriented_to_lps(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 改变 NIfTI 轴排列，核验掩码按物理坐标匹配参考网格。
    @abstractmethod
    def test_nifti_axis_permutation_matches_reference_coordinates(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证 NIfTI 仅部分覆盖参考影像时，未覆盖区域填零。
    @abstractmethod
    def test_partial_nifti_field_of_view_is_zero_padded_on_reference_grid(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证与参考影像完全不重叠的 NIfTI 被拒绝而非静默错位。
    @abstractmethod
    def test_nonoverlapping_nifti_is_rejected_instead_of_silently_misaligning(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 改变 UBD 网格，核验重采样对齐体素支持域的下边界。
    @abstractmethod
    def test_ubd_resampling_aligns_lower_voxel_support_edges(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证 UBD 掩码的物理覆盖范围不匹配时被拒绝。
    @abstractmethod
    def test_ubd_mismatched_field_of_view_is_rejected(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证 UBD 掩码拒绝无效的体素间距。
    @abstractmethod
    def test_ubd_invalid_spacing_is_rejected(
        self, tmp_path: I_FilePath, spacing: float
    ) -> None: ...

    # 验证解码后含非有限标签值的 NIfTI 掩码被拒绝。
    @abstractmethod
    def test_nonfinite_decoded_nifti_labels_are_rejected(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, value: float
    ) -> None: ...

    # 验证维数、内容或大小无效的 UBD 掩码数组被拒绝。
    @abstractmethod
    def test_invalid_ubd_mask_arrays_are_rejected(
        self, tmp_path: I_FilePath, data: NDArray[np.generic]
    ) -> None: ...

    # 验证中文路径 NIfTI 经英文暂存路径读取，完成后清理暂存文件。
    @abstractmethod
    def test_unicode_nifti_is_read_through_ascii_staging_and_cleaned_up(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch, suffix: str
    ) -> None: ...

    # 模拟 NIfTI 读取失败，核验英文路径暂存文件被清理。
    @abstractmethod
    def test_failed_nifti_read_cleans_up_ascii_staging(
        self, tmp_path: I_FilePath, monkeypatch: T_MonkeyPatch
    ) -> None: ...
