from __future__ import annotations

from abc import ABC, abstractmethod

from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath


# 验证影像去重、配套文件命名和不受输出文件影响的来源指纹。
class I_TestSources(ABC):
    # 验证单文件影像的标注和掩码输出与输入文件位于同一目录。
    @abstractmethod
    def test_volume_file_uses_colocated_outputs(
        self, tmp_path: I_FilePath, suffix: str
    ) -> None: ...

    # 验证同一 DICOM 序列的文件与目录入口共享标注路径。
    @abstractmethod
    def test_dicom_file_and_directory_share_annotation(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证生成标注和掩码文件不会改变 DICOM 来源指纹。
    @abstractmethod
    def test_dicom_outputs_do_not_change_source_fingerprint(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证重复影像来源不会产生多个集合项。
    @abstractmethod
    def test_collection_deduplicates_sources(self, tmp_path: I_FilePath) -> None: ...

    # 验证编号后缀不改变影像基名和配套文件所在目录。
    @abstractmethod
    def test_numbered_annotation_paths_preserve_base_and_directory(
        self, tmp_path: I_FilePath, suffix: str, index: int
    ) -> None: ...

    # 验证不同编号的 DICOM 标注文件不影响影像指纹。
    @abstractmethod
    def test_numbered_dicom_annotations_do_not_affect_fingerprint(
        self, tmp_path: I_FilePath
    ) -> None: ...

    # 验证标注路径拒绝负数和无效编号。
    @abstractmethod
    def test_annotation_path_rejects_invalid_indices(
        self, tmp_path: I_FilePath, index: int | float, error: type[Exception]
    ) -> None: ...
