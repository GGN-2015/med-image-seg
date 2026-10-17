from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from med_image_seg.Abstract.Domain.Imaging.E_SourceKind import E_SourceKind

from ...Abstract.Core.I_TestSources import I_TestSources

if TYPE_CHECKING:
    from med_image_seg.Abstract.Storage.Paths.I_FilePath import I_FilePath
from typing import final

import pytest


# 验证影像去重、配套文件命名和不受输出文件影响的来源指纹。
@final
class C_TestSources(I_TestSources):
    # 为当前测试类配置离屏 Qt 环境。
    @pytest.fixture(autouse=True, name="configure_environment")
    def _configure_environment_fixture(self) -> None:
        from ..Environment.C_TestEnvironment import C_TestEnvironment

        C_TestEnvironment().configure()

    # 验证单文件影像的标注和掩码输出与输入文件位于同一目录。
    @pytest.mark.parametrize("suffix", [".nii", ".nii.gz", ".ubd.npz"])
    def test_volume_file_uses_colocated_outputs(
        self, tmp_path: I_FilePath, suffix: str
    ) -> None:
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        image = tmp_path / f"pelvis{suffix}"
        image.write_bytes(b"nifti-test")
        source = C_ImageSourceFactory().from_path(image)
        assert source.getKind() == (
            E_SourceKind.UBD if suffix == ".ubd.npz" else E_SourceKind.NIFTI
        )
        assert source.getAnnotationPath() == tmp_path / "pelvis.med-image-seg.json"
        assert source.getMaskPath() == tmp_path / "pelvis.med-image-seg-mask.nii.gz"
        assert source.getUbdMaskPath() == tmp_path / "pelvis.med-image-seg-mask.ubd.npz"

    # 覆盖十字符边界、复合扩展名和中文名称，显示调整不得改变真实路径。
    @pytest.mark.parametrize("folder", ["case-a", "病例甲"])
    @pytest.mark.parametrize(
        ("filename", "qualified"),
        [
            ("CT.nii", True),
            ("123456.nii", True),
            ("1234567.nii", False),
            ("CT.nii.gz", True),
            ("123.nii.gz", True),
            ("1234.nii.gz", False),
            ("CT.ubd.npz", True),
            ("MRI.ubd.npz", False),
            ("图像.nii", True),
        ],
    )
    def test_short_image_names_include_parent_folder(
        self, tmp_path: I_FilePath, folder: str, filename: str, qualified: bool
    ) -> None:
        from med_image_seg.Concrete.Storage.Volumes import C_ImageSourceFactory

        directory = tmp_path / folder
        directory.mkdir()
        image = directory / filename
        image.write_bytes(b"original image")
        source = C_ImageSourceFactory().from_path(image)
        kind = "UBD" if filename.endswith(".ubd.npz") else "NIFTI"
        label = f"{folder}/{filename}" if qualified else filename
        assert source.getDisplayName() == f"[{kind}] {label}"
        assert source.getPath() == image
        assert source.getAnnotationPath().getParent() == directory
        assert image.read_bytes() == b"original image"

    # 验证同一 DICOM 序列的文件与目录入口共享标注路径。
    def test_dicom_file_and_directory_share_annotation(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        dicom = tmp_path / "IM0001.dcm"
        dicom.write_bytes(b"dicom-test")
        from_file = C_ImageSourceFactory().from_path(dicom)
        from_directory = C_ImageSourceFactory().from_path(tmp_path)
        assert from_file.getKind() == E_SourceKind.DICOM
        assert from_file.getPath() == tmp_path
        assert from_file.getAnnotationPath() == tmp_path / ".med-image-seg.json"
        assert from_file.getMaskPath() == tmp_path / "med-image-seg-mask.nii.gz"
        assert from_file.getUbdMaskPath() == tmp_path / "med-image-seg-mask.ubd.npz"
        assert from_file.getUbdMaskPath() == from_directory.getUbdMaskPath()
        assert from_file.getFingerprint() == from_directory.getFingerprint()

    # 验证生成标注和掩码文件不会改变 DICOM 来源指纹。
    def test_dicom_outputs_do_not_change_source_fingerprint(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        series = tmp_path / "dicom"
        series.mkdir()
        (series / "0001.dcm").write_bytes(b"dicom-1")
        (series / "0002.dcm").write_bytes(b"dicom-2")
        before = C_ImageSourceFactory().from_path(series)
        before.getAnnotationPath().write_text("{}", encoding="utf-8")
        C_FilePath(f"{before.getAnnotationPath()}.bak").write_text(
            "{}", encoding="utf-8"
        )
        before.getMaskPath().write_bytes(b"generated-mask")
        before.getUbdMaskPath().write_bytes(b"generated-ubd-mask")
        (series / "other-output.nii.gz").write_bytes(b"other-generated-mask")
        (series / "other-output.ubd.npz").write_bytes(b"other-generated-ubd-mask")
        (series / "metadata.json").write_text("{}", encoding="utf-8")
        after = C_ImageSourceFactory().from_path(series)
        assert after.getFingerprint() == before.getFingerprint()
        assert after.getSourceId() == before.getSourceId()
        assert "2 files" in after.getDisplayName()

    # 验证重复影像来源不会产生多个集合项。
    def test_collection_deduplicates_sources(self, tmp_path: I_FilePath) -> None:
        from med_image_seg.Concrete.Domain.Collections.C_ImageCollection import (
            C_ImageCollection,
        )

        image = tmp_path / "scan.nii"
        image.write_bytes(b"image")
        collection = C_ImageCollection([image, image])
        assert len(collection) == 1

    # 移除首、中、尾项都只改变集合，保留文件并同步去重索引。
    @pytest.mark.parametrize("index", [0, 1, 2])
    def test_collection_removes_sources_without_deleting_files(
        self, tmp_path: I_FilePath, index: int
    ) -> None:
        from med_image_seg.Concrete.Domain.Collections import C_ImageCollection

        paths = [tmp_path / f"scan-{number}.nii" for number in range(3)]
        for path in paths:
            path.write_bytes(b"unchanged image")
        collection = C_ImageCollection(paths)
        sources = tuple(collection)
        removed = sources[index]
        assert not collection.removeByFingerprint("not-imported")
        assert collection.removeByFingerprint(removed.getFingerprint())
        assert not collection.removeByFingerprint(removed.getFingerprint())
        assert collection.findByFingerprint(removed.getFingerprint()) is None
        assert tuple(collection) == sources[:index] + sources[index + 1 :]
        for source in collection:
            assert collection.findByFingerprint(source.getFingerprint()) is source
        for path in paths:
            assert path.read_bytes() == b"unchanged image"
        reimported = collection.add(paths[index])
        assert len(collection) == 3
        assert collection[2] is reimported
        assert reimported.getFingerprint() == removed.getFingerprint()
        assert collection.add(paths[index]) is reimported
        assert len(collection) == 3

    # 验证编号后缀不改变影像基名和配套文件所在目录。
    @pytest.mark.parametrize("suffix", [".nii", ".nii.gz", ".ubd.npz"])
    @pytest.mark.parametrize("index", [0, 1, 23, 2**80])
    def test_numbered_annotation_paths_preserve_base_and_directory(
        self, tmp_path: I_FilePath, suffix: str, index: int
    ) -> None:
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        image = tmp_path / f"扫描.复查{suffix}"
        image.write_bytes(b"image")
        source = C_ImageSourceFactory().from_path(image)
        number = "" if index == 0 else f"-{index}"
        assert (
            source.annotation_path_for_index(index)
            == tmp_path / f"扫描.复查.med-image-seg{number}.json"
        )
        assert source.annotation_path_for_index(0) == source.getAnnotationPath()

    # 验证不同编号的 DICOM 标注文件不影响影像指纹。
    def test_numbered_dicom_annotations_do_not_affect_fingerprint(
        self, tmp_path: I_FilePath
    ) -> None:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        (tmp_path / "0001.dcm").write_bytes(b"dicom")
        source = C_ImageSourceFactory().from_path(tmp_path)
        for index in (1, 12):
            path = source.annotation_path_for_index(index)
            assert path.getName() == f".med-image-seg-{index}.json"
            for suffix in ("", ".bak", ".tmp", ".bak.tmp"):
                C_FilePath(f"{path}{suffix}").write_text("{}", encoding="utf-8")
        after = C_ImageSourceFactory().from_path(tmp_path)
        assert after.getFingerprint() == source.getFingerprint()
        assert "1 files" in after.getDisplayName()

    # 验证标注路径拒绝负数和无效编号。
    @pytest.mark.parametrize("index, error", [(-1, ValueError), (1.5, TypeError)])
    def test_annotation_path_rejects_invalid_indices(
        self, tmp_path: I_FilePath, index: int | float, error: type[Exception]
    ) -> None:
        from med_image_seg.Concrete.Storage.Volumes.C_ImageSourceFactory import (
            C_ImageSourceFactory,
        )

        image = tmp_path / "scan.nii"
        image.write_bytes(b"image")
        source = C_ImageSourceFactory().from_path(image)
        with pytest.raises(error):
            method_name = "annotation_path_for_index"
            getattr(source, method_name)(index)

    # 把 pytest 临时目录转换为路径接口，供业务测试复用。
    @pytest.fixture(name="tmp_path")
    def _adapt_path(self, tmp_path: Path) -> I_FilePath:
        from med_image_seg.Concrete.Storage.Paths.C_FilePath import C_FilePath

        return C_FilePath(tmp_path)
