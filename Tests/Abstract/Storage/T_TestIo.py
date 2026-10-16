from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath

T_MonkeyPatch = TypeVar("T_MonkeyPatch")


# 验证医学影像与掩码文件读写、几何保留和中文路径兼容。
class T_TestIo(ABC, Generic[T_MonkeyPatch]):
    # 通过正式读取器往返读写 NIfTI，核验掩码及几何一致。
    @abstractmethod
    def test_nifti_round_trip_uses_reader_and_preserves_mask_geometry(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证 NIfTI 先写英文暂存路径，并保留间距和原点。
    @abstractmethod
    def test_nifti_export_uses_ascii_staging_and_preserves_geometry(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        suffix: str,
        directory: str,
        filename: str,
    ) -> None: ...

    # 模拟 NIfTI 导出失败，核验原输出保留且临时文件清理。
    @abstractmethod
    def test_failed_nifti_export_preserves_output_and_cleans_temporary_files(
        self,
        tmp_path: I_FilePath,
        monkeypatch: T_MonkeyPatch,
        failed_step: str,
        existing_output: bool,
    ) -> None: ...

    # 验证默认临时目录不适用时会选择可用的纯英文路径。
    @abstractmethod
    def test_ascii_temporary_directory_falls_back_from_unsuitable_default(
        self, monkeypatch: T_MonkeyPatch, default_kind: str
    ) -> None: ...

    # 验证没有可用英文临时目录时会明确报错。
    @abstractmethod
    def test_ascii_temporary_directory_reports_no_usable_directory(
        self, monkeypatch: T_MonkeyPatch
    ) -> None: ...

    # 通过中文路径往返读写 UBD，核验前景体素不变。
    @abstractmethod
    def test_ubd_round_trip_supports_unicode_paths_and_preserves_mask(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证 UBD 导出拒绝不支持的各向异性间距。
    @abstractmethod
    def test_ubd_export_rejects_anisotropic_spacing(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 生成 DICOM 序列，验证指定读取器正确载入体素及几何。
    @abstractmethod
    def test_dicom_series_loads_through_required_reader(
        self, tmp_path: I_FilePath
    ) -> None: ...
