from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from pytest import MonkeyPatch

from med_image_seg.Abstract.Domain.Imaging.I_ImageSource import I_ImageSource

from ...Abstract.Storage.T_TestIo import T_TestIo

if TYPE_CHECKING:
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
import importlib
from typing import final

import numpy as np
import pytest
import SimpleITK as sitk


# 验证医学影像与掩码文件读写、几何保留和中文路径兼容。
@final
class C_TestIo(T_TestIo[MonkeyPatch]):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 生成已知体素及物理几何的 NIfTI 测试文件。
    def _write_test_nifti(self, path: I_FilePath) -> None:
        from .C_IoFixtures import C_IoFixtures

        return C_IoFixtures().write_test_nifti(path)

    # 生成带完整几何标签的 DICOM 测试序列。
    def _write_test_dicom_series(self, directory: I_FilePath) -> None:
        from .C_IoFixtures import C_IoFixtures

        return C_IoFixtures().write_test_dicom_series(directory)

    # 通过正式读取器往返读写 NIfTI，核验掩码及几何一致。
    def test_nifti_round_trip_uses_reader_and_preserves_mask_geometry(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskWriter import (
            C_MedicalMaskWriter,
        )
        from med_image_seg.Concrete.Storage.Volumes.C_MedicalVolumeReader import (
            C_MedicalVolumeReader,
        )

        from .C_IoFixtures import C_IoFixtures

        source = tmp_path / "scan.nii.gz"
        C_IoFixtures().write_test_nifti(source)
        volume = C_MedicalVolumeReader(1.0).read(source)
        mask = np.zeros(volume.getData().shape, dtype=np.uint8)
        mask[1:-1, 1:-1, 1:-1] = 1
        output = C_MedicalMaskWriter().write(tmp_path / "mask.nii.gz", mask, volume)
        written = sitk.ReadImage(str(str(output)))
        assert volume.getData().ndim == 3
        assert volume.getSpacingMm() == (1.0, 1.0, 1.0)
        assert written.GetSpacing() == volume.getSpacingMm()
        assert written.GetOrigin() == volume.getOriginLpsMm()
        assert written.GetSize() == mask.shape

    # 验证 NIfTI 先写英文暂存路径，并保留间距和原点。
    @pytest.mark.parametrize("suffix", [".nii", ".nii.gz"])
    @pytest.mark.parametrize(
        ("directory", "filename"),
        [
            ("ascii", "mask"),
            ("中文目录", "mask"),
            ("ascii", "掩码"),
            ("中文目录", "掩码"),
        ],
    )
    def test_nifti_export_uses_ascii_staging_and_preserves_geometry(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        suffix: str,
        directory: str,
        filename: str,
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskWriter import (
            C_MedicalMaskWriter,
        )
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        output = tmp_path / directory / f"{filename}{suffix}"
        output.getParent().mkdir()
        output.write_bytes(b"previous mask")
        mask = np.zeros((4, 5, 6), dtype=np.uint8)
        mask[1:3, 2:4, 1:5] = 1
        spacing = (0.8, 0.8, 0.8)
        origin = (-10.0, 20.0, 30.0)
        temporary_paths: list[I_FilePath] = []
        written_bytes: list[bytes] = []
        write_image = sitk.WriteImage

        # 记录并检查 NIfTI 使用的纯英文暂存路径，再调用原写入器。
        def record_write(image: sitk.Image, path: str, *, useCompression: bool) -> None:
            temporary = C_FilePath(path)
            assert str(temporary).isascii()
            assert temporary.getName() == f"mask{suffix}"
            assert temporary != output
            assert useCompression
            temporary_paths.append(temporary)
            write_image(image, path, useCompression=useCompression)
            written = sitk.ReadImage(str(path))
            assert written.GetSize() == mask.shape
            assert written.GetSpacing() == pytest.approx(spacing)
            assert written.GetOrigin() == origin
            assert written.GetDirection() == (
                1.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                1.0,
            )
            np.testing.assert_array_equal(
                np.transpose(sitk.GetArrayFromImage(written), (2, 1, 0)), mask
            )
            written_bytes.append(temporary.read_bytes())

        monkeypatch.setattr(
            importlib.import_module(
                {"sitk": "SimpleITK", "shutil": "shutil", "os": "os"}["sitk"]
            ),
            "WriteImage",
            record_write,
        )
        result = C_MedicalMaskWriter().write_geometry(
            output, mask, spacing_mm=spacing, origin_lps_mm=origin
        )
        assert result == output.resolve()
        assert len(temporary_paths) == 1
        assert output.read_bytes() == written_bytes[0]
        assert not temporary_paths[0].getParent().exists()
        assert list(output.getParent().iterdir()) == [output]

    # 模拟 NIfTI 导出失败，核验原输出保留且临时文件清理。
    @pytest.mark.parametrize("failed_step", ["write", "copy", "replace"])
    @pytest.mark.parametrize("existing_output", [False, True])
    def test_failed_nifti_export_preserves_output_and_cleans_temporary_files(
        self,
        tmp_path: I_FilePath,
        monkeypatch: MonkeyPatch,
        failed_step: str,
        existing_output: bool,
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskWriter import (
            C_MedicalMaskWriter,
        )
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        output = tmp_path / "中文目录" / "掩码.nii.gz"
        output.getParent().mkdir()
        if existing_output:
            output.write_bytes(b"previous mask")
        temporary_paths: list[I_FilePath] = []

        # 模拟 NIfTI 暂存写入失败，记录临时文件以检查清理。
        def fail_write(image: sitk.Image, path: str, *, useCompression: bool) -> None:
            temporary = C_FilePath(path)
            temporary_paths.append(temporary)
            temporary.write_bytes(b"temporary mask")
            if failed_step == "write":
                raise RuntimeError("simulated export failure")

        # 模拟目标目录复制到一半后失败，核验原输出未被破坏。
        def fail_copy(source: I_ImageSource, destination: I_FilePath) -> None:
            temporary_paths.append(destination)
            destination.write_bytes(b"partial copy")
            if failed_step == "copy":
                raise OSError("simulated export failure")

        # 模拟原子替换失败，核验目标文件保护与暂存清理。
        def fail_replace(source: I_ImageSource, destination: I_FilePath) -> None:
            raise OSError("simulated export failure")

        monkeypatch.setattr(
            importlib.import_module(
                {"sitk": "SimpleITK", "shutil": "shutil", "os": "os"}["sitk"]
            ),
            "WriteImage",
            fail_write,
        )
        monkeypatch.setattr(
            importlib.import_module(
                {"sitk": "SimpleITK", "shutil": "shutil", "os": "os"}["shutil"]
            ),
            "copyfile",
            fail_copy,
        )
        monkeypatch.setattr(
            importlib.import_module(
                {"sitk": "SimpleITK", "shutil": "shutil", "os": "os"}["os"]
            ),
            "replace",
            fail_replace,
        )
        with pytest.raises((RuntimeError, OSError), match="simulated export failure"):
            C_MedicalMaskWriter().write_geometry(
                output, np.ones((2, 3, 4), dtype=np.uint8), spacing_mm=(1.0, 1.0, 1.0)
            )
        if existing_output:
            assert output.read_bytes() == b"previous mask"
        else:
            assert not output.exists()
        assert temporary_paths
        assert all(not temporary.getParent().exists() for temporary in temporary_paths)
        assert list(output.getParent().iterdir()) == (
            [output] if existing_output else []
        )

    # 验证默认临时目录不适用时会选择可用的纯英文路径。
    @pytest.mark.parametrize("default_kind", ["unicode", "unwritable"])
    def test_ascii_temporary_directory_falls_back_from_unsuitable_default(
        self, monkeypatch: MonkeyPatch, default_kind: str
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_NiftiPathPolicy import (
            C_NiftiPathPolicy,
        )
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        temporary_directory = importlib.import_module(
            "med_image_seg.Concrete.Storage.Masks.C_NiftiPathPolicy"
        ).TemporaryDirectory
        with C_NiftiPathPolicy().ascii_temporary_directory() as ascii_directory:
            root = C_FilePath(ascii_directory)
            default = root / (
                "中文临时目录" if default_kind == "unicode" else "unwritable"
            )
            default.mkdir()

            # 模拟默认目录不可用，并记录成功回退创建的临时目录。
            def create_directory(
                *, prefix: str, dir: I_FilePath | None
            ) -> TemporaryDirectory[str]:
                assert dir != default or default_kind != "unicode"
                if dir == default:
                    raise PermissionError("simulated unwritable directory")
                return temporary_directory(prefix=prefix, dir=dir)

            with monkeypatch.context() as patch:
                patch.chdir(root)
                patch.setattr(
                    importlib.import_module(
                        "med_image_seg.Concrete.Storage.Masks.C_NiftiPathPolicy"
                    ),
                    "gettempdir",
                    lambda: str(default),
                )
                patch.setattr(
                    importlib.import_module(
                        "med_image_seg.Concrete.Storage.Masks.C_NiftiPathPolicy"
                    ),
                    "TemporaryDirectory",
                    create_directory,
                )
                with C_NiftiPathPolicy().ascii_temporary_directory() as directory:
                    temporary = C_FilePath(directory)
                    assert str(temporary).isascii()
                    assert temporary.getParent() == root
                assert not temporary.exists()

    # 验证没有可用英文临时目录时会明确报错。
    def test_ascii_temporary_directory_reports_no_usable_directory(
        self, monkeypatch: MonkeyPatch
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_NiftiPathPolicy import (
            C_NiftiPathPolicy,
        )

        # 模拟临时目录不可写，检查没有可用候选时的错误提示。
        def deny_directory(*, prefix: str, dir: I_FilePath | None) -> None:
            raise PermissionError("simulated unwritable directory")

        monkeypatch.setattr(
            importlib.import_module(
                "med_image_seg.Concrete.Storage.Masks.C_NiftiPathPolicy"
            ),
            "TemporaryDirectory",
            deny_directory,
        )
        with pytest.raises(OSError, match="writable ASCII-only temporary directory"):
            C_NiftiPathPolicy().ascii_temporary_directory()

    # 通过中文路径往返读写 UBD，核验前景体素不变。
    def test_ubd_round_trip_supports_unicode_paths_and_preserves_mask(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskWriter import (
            C_MedicalMaskWriter,
        )
        from med_image_seg.Concrete.Storage.Volumes.C_MedicalVolumeReader import (
            C_MedicalVolumeReader,
        )

        output = tmp_path / "中文目录" / "掩码.ubd.npz"
        mask = np.zeros((4, 5, 6), dtype=np.uint8)
        mask[1:3, 2:4, 1:5] = 1
        result = C_MedicalMaskWriter().write_geometry(
            output, mask, spacing_mm=(0.8, 0.8, 0.8)
        )
        loaded = C_MedicalVolumeReader(0.8).read(output)
        assert result == output.resolve()
        assert loaded.getSpacingMm() == (0.8, 0.8, 0.8)
        assert loaded.getMetadata().getText("modality") == "MASK"
        np.testing.assert_array_equal(loaded.getData(), mask)
        with np.load(output, allow_pickle=False) as archive:
            assert archive["body_data"].dtype == np.uint8
            assert archive["image_type"].item() == "mask"
            assert archive["mmpd"].item() == 0.8

    # 验证 UBD 导出拒绝不支持的各向异性间距。
    def test_ubd_export_rejects_anisotropic_spacing(self, tmp_path: I_FilePath) -> None:
        from med_image_seg.Concrete.Storage.Masks.C_MedicalMaskWriter import (
            C_MedicalMaskWriter,
        )

        output = tmp_path / "mask.ubd.npz"
        with pytest.raises(ValueError, match="UBD output requires isotropic spacing"):
            C_MedicalMaskWriter().write_geometry(
                output, np.ones((2, 3, 4), dtype=np.uint8), spacing_mm=(0.8, 0.8, 1.0)
            )
        assert not output.exists()

    # 生成 DICOM 序列，验证指定读取器正确载入体素及几何。
    def test_dicom_series_loads_through_required_reader(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Volumes.C_MedicalVolumeReader import (
            C_MedicalVolumeReader,
        )

        from .C_IoFixtures import C_IoFixtures

        directory = tmp_path / "dicom"
        C_IoFixtures().write_test_dicom_series(directory)
        volume = C_MedicalVolumeReader(1.0).read(directory)
        assert volume.getData().ndim == 3
        assert volume.getData().shape[2] >= 4
        assert volume.getMetadata().getText("modality") == "CT"

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
