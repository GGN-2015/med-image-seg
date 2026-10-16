from __future__ import annotations

import shutil
from pathlib import Path
from typing import final

import numpy as np
import pytest
import SimpleITK as sitk
from numpy.typing import NDArray
from pytest import MonkeyPatch

from med_image_seg.Abstract.Domain.Imaging.I_MedicalVolume import I_MedicalVolume
from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

from ...Abstract.Storage.T_TestExternalMaskReader import T_TestExternalMaskReader


# 验证外置掩码的物理对齐、格式校验和中文路径读取。
@final
class C_TestExternalMaskReader(T_TestExternalMaskReader[MonkeyPatch]):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 创建具有已知尺寸、间距和原点的参考影像，用于掩码对齐测试。
    def _reference(
        self,
        tmp_path: I_FilePath,
        shape: tuple[int, int, int] = (6, 5, 4),
        spacing: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ) -> I_MedicalVolume:
        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        return C_ExternalMaskReaderFixtures().reference(tmp_path, shape, spacing)

    # 写入测试掩码及其物理几何，供读取和重采样场景使用。
    def _write(
        self,
        path: I_FilePath,
        data: NDArray[np.generic],
        reference: I_MedicalVolume,
        *,
        spacing: tuple[float, float, float] | None = None,
        origin: tuple[float, float, float] | None = None,
        direction: tuple[float, ...] | None = None,
    ) -> None:
        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        return C_ExternalMaskReaderFixtures().write(
            path, data, reference, spacing=spacing, origin=origin, direction=direction
        )

    # 往返读写外置掩码，验证体素与参考影像网格一致。
    @pytest.mark.parametrize("suffix", [".nii", ".nii.gz", ".ubd.npz"])
    @pytest.mark.parametrize("empty", [False, True])
    def test_external_mask_round_trip_matches_reference_grid(
        self, tmp_path: I_FilePath, suffix: str, empty: bool
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskWriter import (
            C_MedicalMaskWriter,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(
            tmp_path, spacing=(0.8, 0.8, 0.8)
        )
        mask = np.zeros(reference.getData().shape, dtype=np.uint8)
        if not empty:
            mask[1:4, 2:4, 1] = 1
            mask[4, 1, 3] = 1
        path = C_MedicalMaskWriter().write(tmp_path / f"mask{suffix}", mask, reference)
        result = C_MedicalMaskReader().read(path, reference)
        np.testing.assert_array_equal(result, mask)
        assert result.dtype == np.uint8
        assert result.flags.c_contiguous

    # 验证外置掩码的所有非零标签均作为前景显示。
    def test_external_mask_keeps_all_nonzero_labels(self, tmp_path: I_FilePath) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        data = np.zeros(reference.getData().shape, dtype=np.float32)
        data[1, 2, 1] = 7
        data[3, 2, 1] = -3
        data[4, 1, 3] = 0.01
        path = tmp_path / "labels.nii.gz"
        C_ExternalMaskReaderFixtures().write(path, data, reference)
        np.testing.assert_array_equal(
            C_MedicalMaskReader().read(path, reference), data != 0
        )

    # 改变掩码间距及原点，核验最近邻重采样使用物理坐标。
    def test_nifti_resamples_nearest_neighbor_using_physical_origin_and_spacing(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        data = np.zeros((3, 5, 4), dtype=np.float32)
        data[1, 2, 1] = 7
        path = tmp_path / "coarse.nii.gz"
        C_ExternalMaskReaderFixtures().write(
            path, data, reference, spacing=(2.0, 1.0, 1.0), origin=(10.25, -20.0, 30.0)
        )
        result = C_MedicalMaskReader().read(path, reference)
        expected = np.zeros(reference.getData().shape, dtype=np.uint8)
        expected[2:4, 2, 1] = 1
        np.testing.assert_array_equal(result, expected)

    # 翻转 NIfTI 方向，核验读取结果正确重定向到 LPS。
    def test_nifti_direction_flip_is_correctly_reoriented_to_lps(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        data = np.zeros(reference.getData().shape, dtype=np.uint8)
        data[1, 2, 1] = 1
        path = tmp_path / "flipped.nii"
        C_ExternalMaskReaderFixtures().write(
            path,
            data,
            reference,
            origin=(15.0, -20.0, 30.0),
            direction=(-1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
        )
        np.testing.assert_array_equal(
            C_MedicalMaskReader().read(path, reference), data[::-1]
        )

    # 改变 NIfTI 轴排列，核验掩码按物理坐标匹配参考网格。
    def test_nifti_axis_permutation_matches_reference_coordinates(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        data = np.zeros((5, 6, 4), dtype=np.uint8)
        data[2, 4, 1] = 1
        path = tmp_path / "permuted.nii.gz"
        C_ExternalMaskReaderFixtures().write(
            path,
            data,
            reference,
            direction=(0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0),
        )
        expected = np.zeros(reference.getData().shape, dtype=np.uint8)
        expected[4, 2, 1] = 1
        np.testing.assert_array_equal(
            C_MedicalMaskReader().read(path, reference), expected
        )

    # 验证 NIfTI 仅部分覆盖参考影像时，未覆盖区域填零。
    def test_partial_nifti_field_of_view_is_zero_padded_on_reference_grid(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        path = tmp_path / "partial.nii"
        C_ExternalMaskReaderFixtures().write(
            path,
            np.ones((2, 2, 2), dtype=np.uint8),
            reference,
            origin=(12.0, -19.0, 31.0),
        )
        expected = np.zeros(reference.getData().shape, dtype=np.uint8)
        expected[2:4, 1:3, 1:3] = 1
        np.testing.assert_array_equal(
            C_MedicalMaskReader().read(path, reference), expected
        )

    # 验证与参考影像完全不重叠的 NIfTI 被拒绝而非静默错位。
    def test_nonoverlapping_nifti_is_rejected_instead_of_silently_misaligning(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        path = tmp_path / "unrelated.nii"
        C_ExternalMaskReaderFixtures().write(
            path,
            np.ones(reference.getData().shape, dtype=np.uint8),
            reference,
            origin=(1000.0, 1000.0, 1000.0),
        )
        with pytest.raises(ValueError, match="does not overlap"):
            C_MedicalMaskReader().read(path, reference)

    # 改变 UBD 网格，核验重采样对齐体素支持域的下边界。
    def test_ubd_resampling_aligns_lower_voxel_support_edges(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path, shape=(6, 4, 4))
        data = np.zeros((3, 2, 2), dtype=np.uint8)
        data[0, 0, 0] = 3
        path = tmp_path / "coarse.ubd.npz"
        np.savez_compressed(path, body_data=data, mmpd=2.0)
        expected = np.zeros(reference.getData().shape, dtype=np.uint8)
        expected[:2, :2, :2] = 1
        np.testing.assert_array_equal(
            C_MedicalMaskReader().read(path, reference), expected
        )

    # 验证 UBD 掩码的物理覆盖范围不匹配时被拒绝。
    def test_ubd_mismatched_field_of_view_is_rejected(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        path = tmp_path / "unrelated.ubd.npz"
        np.savez_compressed(path, body_data=np.ones((30, 30, 30)), mmpd=2.0)
        with pytest.raises(ValueError, match="field of view"):
            C_MedicalMaskReader().read(path, reference)

    # 验证 UBD 掩码拒绝无效的体素间距。
    @pytest.mark.parametrize("spacing", [0.0, -1.0, np.nan, np.inf])
    def test_ubd_invalid_spacing_is_rejected(
        self, tmp_path: I_FilePath, spacing: float
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        path = tmp_path / "invalid.ubd.npz"
        np.savez_compressed(path, body_data=reference.getData(), mmpd=spacing)
        with pytest.raises(ValueError, match="spacing"):
            C_MedicalMaskReader().read(path, reference)

    # 验证解码后含非有限标签值的 NIfTI 掩码被拒绝。
    @pytest.mark.parametrize("value", [np.nan, np.inf, -np.inf])
    def test_nonfinite_decoded_nifti_labels_are_rejected(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, value: float
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        path = tmp_path / "invalid.nii"
        data = reference.getData().copy()
        data[1, 2, 1] = value
        path.write_bytes(b"mocked NIfTI reader")
        image = sitk.GetImageFromArray(np.transpose(data, (2, 1, 0)))
        image.SetOrigin(reference.getOriginLpsMm())
        monkeypatch.setattr(sitk, "ReadImage", lambda _path: image)
        with pytest.raises(ValueError, match="finite"):
            C_MedicalMaskReader().read(path, reference)

    # 验证维数、内容或大小无效的 UBD 掩码数组被拒绝。
    @pytest.mark.parametrize(
        "data",
        [
            np.zeros((2, 3)),
            np.zeros((2, 0, 3)),
            np.ones((6, 5, 4), dtype=complex),
            np.full((6, 5, 4), "label"),
        ],
    )
    def test_invalid_ubd_mask_arrays_are_rejected(
        self, tmp_path: I_FilePath, data: NDArray[np.generic]
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        path = tmp_path / "invalid.ubd.npz"
        np.savez_compressed(path, body_data=data, mmpd=1.0)
        with pytest.raises(ValueError):
            C_MedicalMaskReader().read(path, reference)

    # 验证中文路径 NIfTI 经英文暂存路径读取，完成后清理暂存文件。
    @pytest.mark.parametrize("suffix", [".nii", ".nii.gz"])
    def test_unicode_nifti_is_read_through_ascii_staging_and_cleaned_up(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch, suffix: str
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        original = tmp_path / f"mask{suffix}"
        C_ExternalMaskReaderFixtures().write(
            original, np.ones(reference.getData().shape, dtype=np.uint8), reference
        )
        directory = tmp_path / "中文掩码"
        directory.mkdir()
        path = directory / f"分割{suffix}"
        shutil.copyfile(original, path)
        read = sitk.ReadImage
        staged = []

        # 检查读取器收到纯英文文件名，并记录暂存文件以核验清理。
        def tracked(filename: str | I_FilePath):
            assert str(filename).isascii()
            staged.append(filename)
            return read(str(filename))

        monkeypatch.setattr(sitk, "ReadImage", tracked)
        result = C_MedicalMaskReader().read(path, reference)
        assert result.all()
        assert staged
        assert all(not C_FilePath(filename).exists() for filename in staged)

    # 模拟 NIfTI 读取失败，核验英文路径暂存文件被清理。
    def test_failed_nifti_read_cleans_up_ascii_staging(
        self, tmp_path: I_FilePath, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskReader import (
            C_MedicalMaskReader,
        )
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        from .C_ExternalMaskReaderFixtures import C_ExternalMaskReaderFixtures

        reference = C_ExternalMaskReaderFixtures().reference(tmp_path)
        path = tmp_path / "invalid.nii"
        path.write_bytes(b"not a NIfTI file")
        staged = []

        # 记录英文暂存路径并模拟读取失败，供后续检查暂存文件清理。
        def fail(filename: str | I_FilePath):
            staged.append(filename)
            raise RuntimeError("invalid image")

        monkeypatch.setattr(sitk, "ReadImage", fail)
        with pytest.raises(RuntimeError, match="invalid image"):
            C_MedicalMaskReader().read(path, reference)
        assert all(not C_FilePath(filename).exists() for filename in staged)

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
